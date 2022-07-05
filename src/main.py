import os
import cv2
import numpy as np
import mcubes
from tqdm import tqdm

RES_MULT = .1
START_IMG = 0
NB_IMG = 255
ISO_LEVEL = 127


class Mesh:
    def __init__(self, vertices, triangles):
        self.vertices = vertices
        self.triangles = triangles
        self.nb_vertices = len(vertices)
        self.nb_triangles = len(triangles)
        print("==>> nb_vertices: ", self.nb_vertices)
        print("==>> self.nb_triangles: ", self.nb_triangles)

    def export(self, filename):
        print(f"exporting mesh to {filename} ... ")
        mcubes.export_obj(self.vertices, self.triangles, filename)
        print(f"exported {filename}")


def gen_mesh(data, iso_level):
    print(f"marching cubes with iso_level {iso_level}")
    vertices, triangles = mcubes.marching_cubes(data, iso_level)
    print("finished marching cubes")
    print(f"vertices: {vertices.shape}")
    print(f"triangles: {triangles.shape}")

    return Mesh(vertices, triangles)


def load_data(finepath):
    image_files = os.listdir(finepath)
    image_files.sort(key=lambda x: int(x.split('.')[0]))  # sort files

    start, end = get_ranges(image_files)
    image_files = image_files[start: end]  # cut the number of files to load if necessary

    print(f"loading images from {finepath}, starting at {image_files[0]} to {image_files[-1]}")

    all_images = []
    for image_file in tqdm(image_files):
        img_path = os.path.join(finepath, image_file)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, None, fx=RES_MULT, fy=RES_MULT)
        # img = img.astype(np.float32)
        # img = (img - 127.0) / 255.0
        all_images.append(img)
    return np.array(all_images)


def get_ranges(image_files):
    nb_images = len(image_files)
    start_in_range = START_IMG < nb_images and START_IMG > 1
    start = START_IMG if (start_in_range) else 0
    end = nb_images if (NB_IMG < 1) else min(NB_IMG + start, nb_images)
    return start, end


if __name__ == "__main__":
    filepath = "G:/Mon Drive/Scolaire/M1_Limoges/stage M1/Work/data/Tomographie/4_processed"

    data = load_data(filepath)

    print("==>> data.shape: ", data.shape)

    mesh = gen_mesh(data, ISO_LEVEL)
    mesh.export("mesh.obj")

    print("Done !")
