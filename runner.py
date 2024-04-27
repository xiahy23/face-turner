import subprocess
import os
import argparse

def main(args):
    conda_env_name=args.conda_env_name
    dir_code1='./DECA/demos/demo_reconstruct.py'
    dir_input='./input'
    dir_obj='./objs'
    conda_cmd = ['conda', 'run', '-n', conda_env_name, 'python', dir_code1, '-i', dir_input, '-s', dir_obj, '--saveDepth', 'True', '--saveObj', 'True', '--rasterizer_type=pytorch3d']
    if args.obj_status==0:
        subprocess.run(conda_cmd)

    dir_code2='./pytorch3d-renderer/render.py'
    dir_output='./output'
    azim=[-30, 0, 30]
    if args.azim180==1:
        azim=[150, 180, 210]
    render_cmd = ['conda', 'run', '-n', conda_env_name, 'python', dir_code2, '-i', dir_obj, '-s', dir_output, '--image_size', str(args.image_size), '--camera_dist', '3', '--elevation', '-30', '0', '30', '--azim_angle', str(azim[0]), str(azim[1]), str(azim[2]), '--fov', str(args.fov), '--camera_dist', str(args.camera_dist)]
    subprocess.run(render_cmd)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='runner')

    parser.add_argument('--conda_env_name', default='pytorch', type=str,
                        help='the name of your conda environment')
    parser.add_argument('--obj_status', default=0, type=int,
                        help='if there exist objs')
    parser.add_argument('--image_size', default=1024, type=int,
                        help='the width or height of the output image')
    parser.add_argument('--fov', default=60, type=int,
                        help='fov is in degrees and represents the horizontal field of view.')
    parser.add_argument('--camera_dist', default=3, type=float,
                        help='the distance between the camera and the 3D model')
    parser.add_argument('--azim180', default=0, type=int,
                        help='for some special models')
    main(parser.parse_args())