from PIL import Image
import os


# 将图片在垂直方向上切分成片段
def split_image_vertically(image_path, output_dir, num_slices=3,overlap_ratio=0.1):
    """"""
    """   默认参数：
    image_path: 原图路径
    output_dir: 切片保存目录
    num_slices: 切分数量
    overlap_ratio: 重叠比例 (0.1 表示 10% 的重叠，防止代码行被拦腰截断)
    return: 切片文件路径列表
    """
    if not os.path.exists(output_dir):  # 检查指定的输出目录 output_dir 是否存在
        os.makedirs(output_dir)  # 如果目录不存在，则递归创建该目录，确保保存路径有效

    img = Image.open(image_path)  # 使用 Image.open 加载 image_path 指定的图片文件到内存对象 img
    w, h = img.size  # 获取图片的尺寸，w 赋值为宽度，h 赋值为高度

    # 每一片的基础高度
    slice_height = h // num_slices  # 计算每一份切片的基础高度（不含重叠部分），总高度 h 整除切分数量 num_slices
    # 重叠的高度像素
    overlap_height = int(slice_height * overlap_ratio)  # 计算重叠区域的像素高度，即 基础高度 * 重叠比例，并转换为整数

    slice_paths = []  # 初始化一个空列表，用于存储后续生成的所有切片文件的完整路径

    for i in range(num_slices):  # 开始循环，遍历每一个切片的索引 i (从 0 到 num_slices - 1)
        # 计算切片的 top 和 bottom
        top = max(0, i * slice_height - (
            overlap_height if i > 0 else 0))  # 计算裁剪区域的上边缘：除了第一片外，其他片都向上延伸 overlap_height 长度以形成重叠，且最小值为 0
        bottom = min(h, (i + 1) * slice_height + (
            overlap_height if i < num_slices - 1 else 0))  # 计算裁剪区域的下边缘：除了最后一片外，其他片都向下延伸 overlap_height 长度，且最大值不超过总高度 h

        # 裁剪
        crop_img = img.crop((0, top, w, bottom))  # 使用 crop 方法裁剪图片，参数为元组 (左, 上, 右, 下)，截取指定区域的图像

        # 保存
        # 构造切片文件名，格式为：slice_索引_原始文件名 (os.path.basename 用于获取文件名部分)
        slice_name = f"slice_{i}_{os.path.basename(image_path)}"
        slice_path = os.path.join(output_dir, slice_name)  # 使用 os.path.join 将输出目录和文件名拼接成完整的文件保存路径
        crop_img.save(slice_path)  # 将裁剪后的图像对象 crop_img 保存到磁盘上的 slice_path 路径
        slice_paths.append(slice_path)  # 将生成的切片路径添加到 slice_paths 列表中

    return slice_paths  # 函数结束，返回包含所有切片文件路径的列表
