import os
import cv2
import numpy as np
import mcubes
from tqdm import tqdm

resolution_mult = 1.0
start_img = 0
nb_img = 255


def march(data, iso_level):

    print(f"marching cubes with iso_level {iso_level}")
    vertices, triangles = mcubes.marching_cubes(data, iso_level)

    print(f"vertices: {vertices.shape}")
    print(f"triangles: {triangles.shape}")
    print(f"successfully created mesh, exporting to obj ...")

    mcubes.export_obj(vertices, triangles, 'output.obj')

    print("done")


def load_data(finepath):
    image_files = os.listdir(finepath)
    nb_images = min(nb_img, len(image_files))
    image_files = image_files[start_img: start_img + nb_img]  # cut the number of files to load if necessary

    # sort the files by number
    image_files.sort(key=lambda x: int(x.split('.')[0]))

    print(f"loading from {image_files[0]} to  {image_files[-1]}")
    all_images = []

    print(f"loading {image_files}")
    for image_file in tqdm(image_files):
        img_path = os.path.join(finepath, image_file)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, None, fx=resolution_mult, fy=resolution_mult)
        # img = img.astype(np.float32)
        # img = (img - 127.0) / 255.0
        # img -= 127
        all_images.append(img)

    return np.array(all_images)


if __name__ == "__main__":
    # np.set_printoptions(threshold=np.inf)
    filepath = "G:/Mon Drive/Scolaire/M1_Limoges/stage M1/Work/data/Tomographie/4_processed"

    data = load_data(filepath)
    # print("==>> images: ", data)
    print("==>> data.shape: ", data.shape)

    march(data, 127)
