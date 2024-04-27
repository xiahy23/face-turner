import os
# os头文件：os指操作系统，该库支持与操作系统交互，比如创建、删除、重命名等cmd中可以进行操作
import sys
# sys头文件：命令行相关，主程序应该用不到
import torch
import numpy as np
import json
# 处理配置文件.json中的信息
import argparse
#处理预输入参数信息
from pytorch3d.io import load_obj
from pytorch3d.structures import Meshes
from pytorch3d.renderer import (
    look_at_view_transform,
    FoVPerspectiveCameras,
    FoVOrthographicCameras,
    Materials,
    RasterizationSettings,
    MeshRenderer,
    MeshRasterizer,
    SoftPhongShader,
    TexturesVertex,
    TexturesAtlas,
    PointsRenderer,
    PointsRasterizationSettings,
    PointsRasterizer
)
import matplotlib.pyplot as plt
import matplotlib
from utils import Params

# 调用GPU/CPU
if torch.cuda.is_available():
    device = torch.device("cuda:0")
    torch.cuda.set_device(device)
else:
    device = torch.device("cpu")

def get_renderer(image_size, dist, device, elev, azim, fov):
    # Initialize the camera with camera distance, elevation, azimuth angle,
    # and image size
    R, T = look_at_view_transform(dist=dist, elev=elev, azim=azim)
    cameras = FoVPerspectiveCameras(device=device, R=R, T=T, fov=fov)
    raster_settings = RasterizationSettings(
        image_size=image_size,
        blur_radius=0.0,
        faces_per_pixel=1,
    )
    # Initialize rasterizer by using a MeshRasterizer class
    rasterizer = MeshRasterizer(
        cameras=cameras,
        raster_settings=raster_settings
    )
    # The textured phong shader interpolates the texture uv coordinates for
    # each vertex, and samples from a texture image.
    shader = SoftPhongShader(device=device, cameras=cameras)
    # Create a mesh renderer by composing a rasterizer and a shader
    renderer = MeshRenderer(rasterizer, shader)
    return renderer

def get_mesh(obj_filename, device):
    verts, faces, aux = load_obj(
        obj_filename,
        device=device,
        load_textures=True,
        create_texture_atlas=True,
        texture_atlas_size=4,
        texture_wrap="repeat"
         )
    # Create a textures object
    atlas = aux.texture_atlas
    # Create Meshes object
    mesh = Meshes(
        verts=[verts],
        faces=[faces.verts_idx],
        textures=TexturesAtlas(atlas=[atlas]),) 
    return mesh

def render_image(renderer, mesh, obj_filename, azim, elev, savefolder):
    image = renderer(mesh)
    out = os.path.normpath(obj_filename).split(os.path.sep)
    mesh_filename = out[-1].split(".")[0]
    dir_to_save = os.path.join(savefolder, mesh_filename)
    os.makedirs(dir_to_save, exist_ok=True)
    sep = '_'
    file_to_save = '{0}{1}{2}{3}{4}{5}{6}{7}'.format(mesh_filename, sep,
                                                     "elev", int(elev),
                                                     sep, "azim",
                                                     int(azim), ".png")
    filename = os.path.join(dir_to_save, file_to_save)
    matplotlib.image.imsave(filename, image[0, ..., :3].cpu().numpy())
    print("Saved image as " + str(filename))


def steps(image_size, dist, device, elev, azim, inputpath, savefolder, fov):
    renderer = get_renderer(image_size, dist, device, elev, azim, fov)
    with os.scandir(inputpath) as entries:
        # 遍历条目
        for entry in entries:
            # 判断是否为文件夹
            if entry.is_dir():
                obj_filename = os.path.join(entry.path,entry.name+'.obj')
                mesh = get_mesh(obj_filename, device)
                render_image(renderer, mesh, obj_filename, azim, elev, savefolder)
    
def main(params):
    savefolder = params.savefolder
    os.makedirs(savefolder, exist_ok=True)
    [steps(params.image_size, params.camera_dist, device, x, y,
                        params.inputpath, params.savefolder, params.fov)
         for x in params.elevation for y in params.azim_angle]
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='pytorch3d render')

    parser.add_argument('-i', '--inputpath', default='./objs', type=str,
                        help='path to the test data, a folder with folders with obj, mlt, and texture in it')
    parser.add_argument('-s', '--savefolder', default='./output', type=str,
                        help='path to the output directory, where images will be stored.')
    parser.add_argument('--image_size', default=1024, type=int,
                        help='the width or height of the output image')
    parser.add_argument('--camera_dist', default=1, type=float,
                        help='the distance between the camera and the 3D model')
    parser.add_argument('--elevation', nargs='+', default=[-30, 0, 30], type=int,
                        help='')
    parser.add_argument('--azim_angle', nargs='+', default=[-30, 0, 30], type=int,
                        help='')
    parser.add_argument('--fov', default=60, type=int,
                        help='Fov is in degrees and represents the horizontal field of view.')
    main(parser.parse_args())