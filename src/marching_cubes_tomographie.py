import os
import re
import time

import cv2
import mcubes
import numpy as np
from absl import app, flags
from tqdm import tqdm

# becarful of accents in the path
flags.DEFINE_string("INPUT_PATH", "./data/KPP_Brut_AHPCS_dilue_TT_1000/",
                    help="Input image folder")

flags.DEFINE_string("OUTPUT_FILE", "KPP_Brut_AHPCS_dilue_TT_1000.obj",
                    help="Output mesh file")

flags.DEFINE_integer("START_IMG", 0, help="Start image")

flags.DEFINE_integer("NB_IMG", 50, help="Number of images to load")

flags.DEFINE_float("RES_MULT", 0.5, help="Image resolution multiplier")

flags.DEFINE_integer("ISO_LEVEL", 127, help="Iso level")

flags.DEFINE_bool("PADD", True, help="Pad the whole images sequence with black borders")

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
    image_sequence = os.listdir(filepath)

    image_sequence.sort(key=lambda x: int(re.sub("[^0-9]", "", x)))  # sort files by number

    start, end = get_ranges(image_sequence)
    image_sequence = image_sequence[start: end]  # cut the number of files to load if necessary

    if (image_sequence is None or len(image_sequence) == 0):
        print("No image sequence found in the specified folder")
        return None

    # loading an image to get the x and y sizes
    img_temp = cv2.imread(os.path.join(filepath, image_sequence[0]))
    resX = round(img_temp.shape[1] * FLAGS.RES_MULT)
    resY = round(img_temp.shape[0] * FLAGS.RES_MULT)

    print(f"\nloading images from {filepath}, starting at {image_sequence[0]} to {image_sequence[-1]}")
    all_images = []

    if (FLAGS.PADD):
        resX += 2
        resY += 2
        all_images.append(np.zeros((resY, resX), dtype=np.uint8))

    for image_file in tqdm(image_sequence):
        img_path = os.path.join(filepath, image_file)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, None, fx=FLAGS.RES_MULT, fy=FLAGS.RES_MULT)

        if FLAGS.PADD:  # padd the image with black borders
            img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)

        all_images.append(img)

    if (FLAGS.PADD):
        all_images.append(np.zeros((resY, resX), dtype=np.uint8))

    all_images = np.reshape(all_images, (len(image_sequence) + 2 * FLAGS.PADD, resY, resX))

    # roll 90 degrees on Y axis to get the correct orientation
    all_images = np.rollaxis(all_images, 1, 0)

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
        t1 = t + 1
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
