import torch


# def make_batch_tensor(tensor_list):
#     n_tensor = len(tensor_list)
#     t = tensor_list[0].unsqueeze(0)
#     for i in range(1, n_tensor):
#         temp = tensor_list[i].unsqueeze(0)
#         t = torch.cat([t, temp], dim=0)
#
#     return t


def make_batch(datas, category=None):
    if category is None:
        data_batch = datas[0].unsqueeze(0)
        i = 1
        while i < len(datas):
            temp = datas[i].unsqueeze(0)
            data_batch = torch.cat([data_batch, temp], dim=0)
            i += 1
    else:
        data_batch = datas[0][category][0].unsqueeze(0)
        i = 1
        while i < len(datas):
            temp = datas[i][category][0].unsqueeze(0)
            data_batch = torch.cat([data_batch, temp], dim=0)
            i += 1

    return data_batch


def make_pretrain_annotation_batch(anns, ann_category):
    print(anns[0][ann_category])
    ann_batch = anns[0][ann_category].unsqueeze(0)
    for i in range(1, len(anns)):
        temp = anns[i][ann_category].unsqueeze(0)
        ann_batch = torch.cat([ann_batch, temp], dim=0)

    return ann_batch


def crop_center(in_tensor, crop_size):
    h_in, w_in = in_tensor.shape[2], in_tensor.shape[3]
    h_out, w_out = crop_size
    h_drop, w_drop = (h_in - h_out) // 2, (w_in - w_out) // 2

    out_tensor = in_tensor[:, :, h_drop:-h_drop, w_drop:-w_drop]

    return out_tensor


def pad_4dim(x, ref, cuda=True):
    zeros = torch.zeros(x.shape[0], x.shape[1], 1, x.shape[3])
    if cuda:
        zeros = zeros.cuda()
    while x.shape[2] < ref.shape[2]:
        x = torch.cat([x, zeros], dim=2)
    zeros = torch.zeros(x.shape[0], x.shape[1], x.shape[2], 1)
    if cuda:
        zeros = zeros.cuda()
    while x.shape[3] < ref.shape[3]:
        x = torch.cat([x, zeros], dim=3)

    return x


def pad_3dim(x, ref_size):
    zeros = torch.zeros(x.shape[0], 1, x.shape[2]).cuda()
    while x.shape[1] < ref_size[0]:
        x = torch.cat([x, zeros], dim=1)
    zeros = torch.zeros(x.shape[0], x.shape[1], 1).cuda()
    while x.shape[2] < ref_size[1]:
        x = torch.cat([x, zeros], dim=2)

    return x


def pad_2dim(x, ref_size):
    zeros = torch.zeros(1, x.shape[1], dtype=torch.long).cuda()
    while x.shape[0] < ref_size[0]:
        x = torch.cat([x, zeros], dim=0)
    zeros = torch.zeros(x.shape[0], 1, dtype=torch.long).cuda()
    while x.shape[1] < ref_size[1]:
        x = torch.cat([x, zeros], dim=1)

    return x


def mirrored_padding(image, out_size):
    img = image

    c_img, h_img, w_img = img.shape
    h_out, w_out = out_size
    pad_h, pad_w = int((h_out - h_img) / 2), int((w_out - w_img) / 2)

    out_tensor = torch.zeros(c_img, out_size[0], out_size[1])
    out_tensor[:, pad_h:-pad_h, pad_w:-pad_w] = img

    # Up, Down padding
    out_tensor[:, :pad_h, pad_w:-pad_w] = torch.flip(img[:, :pad_h, :], [1])
    out_tensor[:, -pad_h:, pad_w:-pad_w] = torch.flip(img[:, -pad_h:, :], [1])

    # Left, Right padding
    out_tensor[:, pad_h:-pad_h, :pad_w] = torch.flip(img[:, :, :pad_w], [2])
    out_tensor[:, pad_h:-pad_h, -pad_w:] = torch.flip(img[:, :, -pad_w:], [2])

    # Top left, right padding
    out_tensor[:, :pad_h, :pad_w] = torch.flip(img[:, :pad_h, :pad_w], [1, 2])
    out_tensor[:, :pad_h, -pad_w:] = torch.flip(img[:, :pad_h, -pad_w:], [1, 2])

    # Bottom left, right padding
    out_tensor[:, -pad_h:, :pad_w] = torch.flip(img[:, -pad_h:, :pad_w], [1, 2])
    out_tensor[:, -pad_h:, -pad_w:] = torch.flip(img[:, -pad_h:, -pad_w:], [1, 2])

    return out_tensor


def pad_4dim(x, ref):
    device = x.device
    zeros = torch.zeros(x.shape[0], x.shape[1], 1, x.shape[3]).to(device)
    while x.shape[2] < ref.shape[2]:
        x = torch.cat([x, zeros], dim=2)
    zeros = torch.zeros(x.shape[0], x.shape[1], x.shape[2], 1).to(device)
    while x.shape[3] < ref.shape[3]:
        x = torch.cat([x, zeros], dim=3)

    return x


def pad_3dim(x, ref_size):
    zeros = torch.zeros(x.shape[0], 1, x.shape[2]).cuda()
    while x.shape[1] < ref_size[0]:
        x = torch.cat([x, zeros], dim=1)
    zeros = torch.zeros(x.shape[0], x.shape[1], 1).cuda()
    while x.shape[2] < ref_size[1]:
        x = torch.cat([x, zeros], dim=2)

    return x


def pad_2dim(x, ref_size):
    zeros = torch.zeros(1, x.shape[1], dtype=torch.long).cuda()
    while x.shape[0] < ref_size[0]:
        x = torch.cat([x, zeros], dim=0)
    zeros = torch.zeros(x.shape[0], 1, dtype=torch.long).cuda()
    while x.shape[1] < ref_size[1]:
        x = torch.cat([x, zeros], dim=1)

    return x


def calculate_ious(box1, box2):
    device = box1.device

    b1, b2 = box1, box2

    y1_b1 = b1[..., 0]
    x1_b1 = b1[..., 1]
    y2_b1 = b1[..., 2]
    x2_b1 = b1[..., 3]

    y1_b2 = b2[..., 0]
    x1_b2 = b2[..., 1]
    y2_b2 = b2[..., 2]
    x2_b2 = b2[..., 3]

    y1_inter = torch.max(y1_b1, y1_b2)
    x1_inter = torch.max(x1_b1, x1_b2)
    y2_inter = torch.min(y2_b1, y2_b2)
    x2_inter = torch.min(x2_b1, x2_b2)

    h_inter = y2_inter - y1_inter
    h_inter = torch.max(torch.zeros(h_inter.shape).to(device), h_inter)
    w_inter = x2_inter - x1_inter
    w_inter = torch.max(torch.zeros(w_inter.shape).to(device) , w_inter)

    area_b1 = (y2_b1 - y1_b1) * (x2_b1 - x1_b1)
    area_b2 = (y2_b2 - y1_b2) * (x2_b2 - x1_b2)
    area_inter = h_inter * w_inter
    area_union = area_b1 + area_b2 - area_inter

    iou = area_inter / area_union

    return iou




def calculate_iou(box1, box2, dim=0):
    """ Ablelable until 3-dim
    :param box1: tensor, [(y1, x1, y2, x2)]
    :param box2: tensor, [(y1, x1, y2, x2)]
    :param dim: int

    :return:
    """

    # y1_inter = torch.max(box1[..., 0], box2[..., 0], dim=-1)
    # x1_inter = torch.max(box1[..., 1], box2[..., 1], dim=-1)
    # y2_inter = torch.min(box1[..., 2], box2[..., 2], dim=-1)
    # x2_inter = torch.min(box1[..., 3], box2[..., 3], dim=-1)
    #
    # area_inter = (y2_inter - y1_inter) * (x2_inter - x1_inter)
    #
    # area_box1 = (box1[..., 2] - box1[..., 0]) * (box1[..., 3] - box1[..., 1])
    # area_box2 = (box2[..., 2] - box2[..., 0]) * (box2[..., 3] - box2[..., 1])
    # area_union = area_box1 + area_box2 - area_inter
    #
    # iou = area_inter / area_union

    # print(box1, box2)

    if dim == 0:
        y1_inter = torch.max(box1[0], box2[0])
        x1_inter = torch.max(box1[1], box2[1])
        y2_inter = torch.min(box1[2], box2[2])
        x2_inter = torch.min(box1[3], box2[3])

        area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area_box2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

    elif dim == 1:
        y1_inter = torch.max(box1[:, 0], box2[:, 0])
        x1_inter = torch.max(box1[:, 1], box2[:, 1])
        y2_inter = torch.min(box1[:, 2], box2[:, 2])
        x2_inter = torch.min(box1[:, 3], box2[:, 3])

        area_box1 = (box1[:, 2] - box1[:, 0]) * (box1[:, 3] - box1[:, 1])
        area_box2 = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])

    elif dim == 2:
        y1_inter = torch.max(box1[:, :, 0], box2[:, :, 0])
        x1_inter = torch.max(box1[:, :, 1], box2[:, :, 1])
        y2_inter = torch.min(box1[:, :, 2], box2[:, :, 2])
        x2_inter = torch.min(box1[:, :, 3], box2[:, :, 3])

        area_box1 = (box1[:, :, 2] - box1[:, :, 0]) * (box1[:, :, 3] - box1[:, :, 1])
        area_box2 = (box2[:, :, 2] - box2[:, :, 0]) * (box2[:, :, 3] - box2[:, :, 1])

    area_inter = torch.nn.ReLU()(y2_inter - y1_inter) * torch.nn.ReLU()(x2_inter - x1_inter)
    area_union = area_box1 + area_box2 - area_inter

    iou = area_inter / area_union

    return iou


def mean_iou_seg_argmax_pytorch(a, b):
    a = a.argmax(dim=1)
    b = b.argmax(dim=1)
    n_batch = a.shape[0]

    iou_sum = 0
    for batch in range(n_batch):
        a_batch, b_batch = a[batch], b[batch]

        # a_area = (a_batch > 0).sum()
        # b_area = (b_batch > 0).sum()
        # bg_area = ((a_batch == 0) & (b_batch == 0)).sum()
        # inter = (a_batch == b_batch).sum() - bg_area
        # union = a_area + b_area - inter

        a_area = (a_batch == 1).sum()
        b_area = (b_batch == 1).sum()
        bg_area = ((a_batch == 0) & (b_batch == 0)).sum()
        inter = (a_batch == b_batch).sum() - bg_area
        union = a_area + b_area - inter

        iou_temp = torch.true_divide(inter, union)
        iou_sum += iou_temp

        # print('({}, {}) '.format(a_area, b_area), end='')

    iou = torch.true_divide(iou_sum, n_batch)

    return iou


def mean_iou_seg_argmax_voc_pytorch(predict, ground_truth, n_class):
    pred, gt = predict, ground_truth
    # pred = pred.argmax(dim=1)
    # gt = gt.argmax(dim=1)
    n_batch = pred.shape[0]

    iou_sum = 0
    n_obj = 0
    for batch in range(n_batch):
        pred_batch, gt_batch = pred[batch], gt[batch]

        # a_area = (a_batch > 0).sum()
        # b_area = (b_batch > 0).sum()
        # bg_area = ((a_batch == 0) & (b_batch == 0)).sum()
        # inter = (a_batch == b_batch).sum() - bg_area
        # union = a_area + b_area - inter

        for c in range(1, n_class):
            pred_obj = (pred_batch == c)
            gt_obj = (gt_batch == c)
            pred_area = pred_obj.sum()
            gt_area = gt_obj.sum()
            if gt_area == 0:
                continue
            n_obj += 1

            bg_area = ((pred_obj == 0) & (gt_obj == 0)).sum()
            inter = (pred_obj == gt_obj).sum() - bg_area
            union = pred_area + gt_area - inter
            # print('a_area: {}, b_area: {}, bg_area: {}, inter: {}, union: {}'.format(pred_area.item(), gt_area.item(), bg_area.item(), inter.item(), union.item()))

            iou = torch.true_divide(inter, union)
            # print('{} class iou: {}'.format(c, iou))
            iou_sum += iou

    mean_iou = torch.true_divide(iou_sum, n_obj)


        # a_area = (a_batch == 1).sum()
        # b_area = (b_batch == 1).sum()
        # bg_area = ((a_batch == 0) & (b_batch == 0)).sum()
        # inter = (a_batch == b_batch).sum() - bg_area
        # union = a_area + b_area - inter
        #
        # iou_temp = torch.true_divide(inter, union)
        # iou_sum += iou_temp

        # print('({}, {}) '.format(a_area, b_area), end='')

    # iou = torch.true_divide(iou_sum, n_batch)

    return mean_iou


def mean_iou_seg_argmin_pytorch(a, b):
    a = a.argmin(dim=1)
    # b = b.argmin(dim=1)
    n_batch = a.shape[0]

    iou_sum = 0
    for batch in range(n_batch):
        a_batch, b_batch = a[batch], b[batch]

        a_area = (a_batch > 0).sum()
        b_area = (b_batch > 0).sum()
        bg_area = ((a_batch == 0) & (b_batch == 0)).sum()
        inter = (a_batch == b_batch).sum() - bg_area
        union = a_area + b_area - inter

        iou_temp = torch.true_divide(inter, union)
        iou_sum += iou_temp

        # print('({}, {}) '.format(a_area, b_area), end='')

    iou = torch.true_divide(iou_sum, n_batch)

    return iou


def convert_box_from_yxhw_to_yxyx(bbox):
    """
    :param bbox: tensor, [..., (cy, cx, h, w)]
    :return: tensor, [..., (y1, x1, y2, x2)]
    """

    cy, cx, h, w = bbox[..., 0], bbox[..., 1], bbox[..., 2], bbox[..., 3]
    y1, x1, y2, x2 = cy - .5 * h, cx - .5 * w, cy + .5 * h, cx + .5 * w
    y1, x1, y2, x2 = y1.unsqueeze(-1), x1.unsqueeze(-1), y2.unsqueeze(-1), x2.unsqueeze(-1)

    return torch.cat([y1, x1, y2, x2], dim=-1)


def convert_box_from_yxyx_to_yxhw(bbox):
    """
        :param bbox: tensor, [..., (y1, x1, y2, x2)]
        :return: tensor, [..., (cy, cx, h, w)]
    """

    y1, x1, y2, x2 = bbox[..., 0], bbox[..., 1], bbox[..., 2], bbox[..., 3]
    cy, cx, h, w = (y1 + y2) / 2, (x1 + x2) / 2, y2 - y1, x2 - x1
    cy, cx, h, w = cy.unsqueeze(-1), cx.unsqueeze(-1), h.unsqueeze(-1), w.unsqueeze(-1)

    return torch.cat([cy, cx, h, w], dim=-1)


def non_maximum_suppression(bounding_boxes, scores, threshold):
    """
    :param bounding_boxes: tensor, [-1, 4]
    :param scores: tensor, [-1]
    :param threshold: float
    :return: list, [-1, 4]
    """
    bboxes = bounding_boxes

    _, indices = torch.sort(scores, descending=True)
    bboxes = bboxes[indices]
    bboxes_result = []

    base = bboxes[0]
    bboxes_result.append(base)
    for i in range(1, len(bboxes)):
        iou = calculate_iou(base, bboxes[i])
        if iou < threshold:
            bboxes_result.append(bboxes[i])

    return bboxes_result


if __name__ == '__main__':
    pass































