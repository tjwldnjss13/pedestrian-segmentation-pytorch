import torch
import torch.nn as nn

from utils.pytorch_util import *


class NMS(nn.Module):
    def __init__(self):
        super(NMS, self).__init__()
        self.iou_threshold = .7

    def forward(self, bounding_box, cls_score):
        """
        :param bounding_box: Tensor, [num rois, (y1, x1, y2, x2)]
        :param cls_score: Tensor, [num rois]
        :return bbox_keep: Tensor, [num rois after nms, (y1, x1, y2, x2)]
        """
        print('NMS started.')

        bbox = bounding_box[0]
        score = cls_score[0]

        keep = [True for _ in range(len(bbox))]
        score, idx = torch.sort(score, descending=True)
        bbox = bbox[idx]

        for i in range(len(bbox) - 1):
            ious = calculate_ious(bbox[i+1:], bbox[i])
            for j, iou in enumerate(ious):
                if iou > self.iou_threshold:
                    keep[i+j+1] = False

        bbox_keep = bbox[keep]

        print('NMS ended.')

        return bbox_keep




def test():
    bounding_box = torch.Tensor([1, 2, 3, 4]).repeat(10, 1)
    cls_score = torch.Tensor([1, 3, 7, 2, 35, 7254, 754, 34, 86, 153])
    keep = [True for _ in range(len(bounding_box))]

    score, idx = torch.sort(cls_score, descending=True)
    bbox = bounding_box[idx]

    for i in range(len(bbox) - 1):
        ious = calculate_ious(bbox[i + 1:], bbox[i])
        for j, iou in enumerate(ious):
            if iou > .7:
                keep[i + j + 1] = False


if __name__ == '__main__':
    test()

























