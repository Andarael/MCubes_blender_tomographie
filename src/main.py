import os
import cv2
import numpy as np
import mcubes
from tqdm import tqdm
from absl import app, flags
import time
import re

flags.DEFINE_string("INPUT_PATH", "G:\Mon Drive\Scolaire\M1_Limoges\stage M1\Work\data\Tomographie\KPP_Prop_non_impregne", help="Input image folder")

flags.DEFINE_string("OUTPUT_FILE", "mesh.obj", help="Output mesh file")

flags.DEFINE_integer("START_IMG", 0, help="Start image")

flags.DEFINE_integer("NB_IMG", 0, help="Number of images to load")

flags.DEFINE_float("RES_MULT", 0.5, help="Image resolution multiplier")

flags.DEFINE_integer("ISO_LEVEL", 127, help="Iso level")

flags.DEFINE_bool("PADD", True, help="Pad the images sequence with black borders")

FLAGS = flags.FLAGS


class Mesh:
    def __init__(self, vertices, triangles):
        self.vertices = vertices
        self.triangles = triangles
        self.nb_vertices = len(vertices)
        self.nb_triangles = len(triangles)
        print(f"Mesh created with : {self.nb_vertices} vertices and {self.nb_triangles} triangles \n")

    def export(self, filename):
        print(f"exporting mesh to {filename} ... ")
        export_obj(self.vertices, self.triangles, filename)
        # mcubes.export_obj(self.vertices, self.triangles, filename)  # slower
        print(f"exported {filename} !")


def gen_mesh(data, iso_level):
    print(f"Starting marching cubes with iso_level {iso_level} ...")
    start = time.time()
    vertices, triangles = mcubes.marching_cubes(data, iso_level)
    elapsed = time.time() - start
    print(f"finished marching cubes in {elapsed:.2f} seconds")

    return Mesh(vertices, triangles)


def load_data(filepath):
    image_files = os.listdir(filepath)

    image_files.sort(key=lambda x: int(re.sub("[^0-9]", "", x)))  # sort files by number

    start, end = get_ranges(image_files)
    image_files = image_files[start: end]  # cut the number of files to load if necessary

    if (image_files is None or len(image_files) == 0):
        print("No image files found in the specified folder")
        return None

    img_temp = cv2.imread(os.path.join(filepath, image_files[0]))
    resX = round(img_temp.shape[1] * FLAGS.RES_MULT)
    resY = round(img_temp.shape[0] * FLAGS.RES_MULT)

    print(f"\nloading images from {filepath}, starting at {image_files[0]} to {image_files[-1]}")
    all_images = []

    if (FLAGS.PADD):
        all_images.append(np.zeros((resY, resX), dtype=np.uint8))

    for image_file in tqdm(image_files):
        img_path = os.path.join(filepath, image_file)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, None, fx=FLAGS.RES_MULT, fy=FLAGS.RES_MULT)
        all_images.append(img)

    if (FLAGS.PADD):
        all_images.append(np.zeros((resY, resX), dtype=np.uint8))

    all_images = np.reshape(all_images, (len(image_files) + 2*FLAGS.PADD, resY, resX))

    print("\n")
    return all_images


def export_obj(vertices, triangles, filename):
    # Fastest so far (but ~10% slower with progress bar)
    f = open(filename, 'w')
    f.write("# obj file exported from marching cube script\n")

    pbar = tqdm(total=100)
    step = (len(vertices) + len(triangles)) // 100

    for i, v in enumerate(vertices):
        f.write("v %.2f %.2f %.2f\n" % (v[0], v[1], v[2]))
        if (i % step == 0):
            pbar.update(1)

    for i, t in enumerate(triangles):
        t1 = t+1
        f.write("f %d %d %d\n" % (t1[0], t1[1], t1[2]))
        if (i % step == 0 and pbar.n < 100):  # second condition is to stop the progress bar at 100%
            pbar.update(1)

    pbar.close()

    f.close()


def get_ranges(image_files):
    nb_images = len(image_files)
    start_in_range = FLAGS.START_IMG < nb_images and FLAGS.START_IMG > 1
    start = FLAGS.START_IMG if (start_in_range) else 0
    end = nb_images if (FLAGS.NB_IMG < 1) else min(FLAGS.NB_IMG + start, nb_images)
    return start, end


def main(argv):
    data = load_data(FLAGS.INPUT_PATH)
    mesh = gen_mesh(data, FLAGS.ISO_LEVEL)
    mesh.export(FLAGS.OUTPUT_FILE)

    print("\nDone !")


if __name__ == "__main__":
    app.run(main)
