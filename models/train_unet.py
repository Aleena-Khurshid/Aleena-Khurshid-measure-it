"""Train a small U-Net from scratch on the fixed split (CPU only).

Why this model: a U-Net is a small convolutional network that outputs a
mask the same size as the input. It is light enough for a CPU-only laptop
(no NVIDIA GPU), and it is not Ultralytics YOLO and not Roboflow.
Training uses only the train split. The val split chooses the best epoch.
The test split is used once, at the end, for the reported numbers.

Augmentation: horizontal flip of TRAINING images only. Flipped copies are
never counted as photographs and never appear in val or test.
"""
import csv, hashlib, json, random, sys
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = "dataset"
SEED = 42
EPOCHS = 40
W, H = 160, 120
torch.manual_seed(SEED)
random.seed(SEED)
torch.set_num_threads(4)


def load(split_name, ids_by_split):
    xs, ys = [], []
    for pid in ids_by_split[split_name]:
        img = cv2.imread(f"{ROOT}/images/{pid}.jpg")
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mask = cv2.imread(f"{ROOT}/masks/{pid}.png", 0)
        mask = cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)
        xs.append(img.astype(np.float32) / 255.0)
        ys.append((mask > 127).astype(np.float32))
    x = torch.tensor(np.stack(xs)).permute(0, 3, 1, 2)
    y = torch.tensor(np.stack(ys)).unsqueeze(1)
    return x, y


def block(i, o):
    return nn.Sequential(
        nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
        nn.Conv2d(o, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
    )


class SmallUNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.d1, self.d2, self.d3 = block(3, 16), block(16, 32), block(32, 64)
        self.bott = block(64, 96)
        self.u3 = nn.ConvTranspose2d(96, 64, 2, stride=2)
        self.c3 = block(128, 64)
        self.u2 = nn.ConvTranspose2d(64, 32, 2, stride=2)
        self.c2 = block(64, 32)
        self.u1 = nn.ConvTranspose2d(32, 16, 2, stride=2)
        self.c1 = block(32, 16)
        self.out = nn.Conv2d(16, 1, 1)

    def forward(self, x):
        e1 = self.d1(x)
        e2 = self.d2(F.max_pool2d(e1, 2))
        e3 = self.d3(F.max_pool2d(e2, 2))
        b = self.bott(F.max_pool2d(e3, 2))
        d3 = self.c3(torch.cat([self.u3(b), e3], 1))
        d2 = self.c2(torch.cat([self.u2(d3), e2], 1))
        d1 = self.c1(torch.cat([self.u1(d2), e1], 1))
        return self.out(d1)


def loss_fn(logits, y):
    bce = F.binary_cross_entropy_with_logits(logits, y)
    p = torch.sigmoid(logits)
    inter = (p * y).sum()
    dice = 1 - (2 * inter + 1) / (p.sum() + y.sum() + 1)
    return bce + dice


def metrics(logits, y):
    pred = (torch.sigmoid(logits) > 0.5).float()
    tp = (pred * y).sum().item()
    fp = (pred * (1 - y)).sum().item()
    fn = ((1 - pred) * y).sum().item()
    iou_per_img = []
    for p, t in zip(pred, y):
        inter = (p * t).sum().item()
        union = ((p + t) > 0).float().sum().item()
        iou_per_img.append(inter / union if union else 0.0)
    return {
        "mask_iou_mean": float(np.mean(iou_per_img)),
        "pixel_precision": tp / (tp + fp) if tp + fp else 0.0,
        "pixel_recall": tp / (tp + fn) if tp + fn else 0.0,
    }


def main():
    ids_by_split = {"train": [], "val": [], "test": []}
    for r in csv.DictReader(open(f"{ROOT}/split_v3.csv")):
        ids_by_split[r["split"]].append(r["id"])
    print({k: len(v) for k, v in ids_by_split.items()})

    xtr, ytr = load("train", ids_by_split)
    xva, yva = load("val", ids_by_split)
    xte, yte = load("test", ids_by_split)
    # Training-only augmentation: horizontal flip copies of the train set.
    xtr = torch.cat([xtr, torch.flip(xtr, dims=[3])])
    ytr = torch.cat([ytr, torch.flip(ytr, dims=[3])])

    model = SmallUNet()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    best_val, best_state, log = -1, None, []
    for ep in range(1, EPOCHS + 1):
        model.train()
        perm = torch.randperm(len(xtr))
        total = 0.0
        for i in range(0, len(xtr), 8):
            idx = perm[i:i + 8]
            opt.zero_grad()
            loss = loss_fn(model(xtr[idx]), ytr[idx])
            loss.backward()
            opt.step()
            total += loss.item() * len(idx)
        model.eval()
        with torch.no_grad():
            vm = metrics(model(xva), yva)
        log.append({"epoch": ep, "train_loss": total / len(xtr), **vm})
        print(f"epoch {ep:02d} loss {total/len(xtr):.4f} val_iou {vm['mask_iou_mean']:.4f}", flush=True)
        if vm["mask_iou_mean"] > best_val:
            best_val = vm["mask_iou_mean"]
            best_state = {k: v.clone() for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        test = metrics(model(xte), yte)
    torch.save(best_state, "models/unet_small.pt")
    sha = hashlib.sha256(open("models/unet_small.pt", "rb").read()).hexdigest()
    report = {
        "architecture": "small U-Net, 3 down levels, 16/32/64/96 channels, trained from scratch",
        "input_size": [W, H],
        "epochs": EPOCHS,
        "best_val_mask_iou": best_val,
        "test_metrics_once": test,
        "weights_sha256": sha,
        "train_images_with_flips": len(xtr),
        "val_images": len(xva),
        "test_images": len(xte),
        "log": log,
    }
    json.dump(report, open("models/training_report.json", "w"), indent=2)
    print("TEST", json.dumps(test))
    print("sha256", sha)


if __name__ == "__main__":
    main()
