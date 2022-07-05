import os
import cv2
import numpy as np
import mcubes
from tqdm import tqdm
from absl import app, flags

flags.DEFINE_string("INPUT_PATH", default="G:/Mon Drive/Scolaire/M1_Limoges/stage M1/Work/data/Tomographie/4_processed", help="Input image folder")
flags.DEFINE_string("OUTPUT_FILE", default="mesh.obj", help="Output mesh file")

flags.DEFINE_integer("START_IMG", default=0, help="Start image")
flags.DEFINE_integer("NB_IMG", default=0, help="Number of images to load")

flags.DEFINE_float("RES_MULT", default=0.5, help="Image resolution multiplier")
flags.DEFINE_integer("ISO_LEVEL", default=127, help="Iso level")

FLAGS = flags.FLAGS


class Mesh:
    def __init__(self, vertices, triangles):
        self.vertices = vertices
        self.triangles = triangles
        self.nb_vertices = len(vertices)
        self.nb_triangles = len(triangles)
        print("==>> nb_vertices: ", self.nb_vertices)
        print("==>> nb_triangles: ", self.nb_triangles)

    def export(self, filename):
        print(f"exporting mesh to {filename} ... ")
        mcubes.export_obj(self.vertices, self.triangles, filename)
        print(f"exported {filename}")


def gen_mesh(data, iso_level):
    print(f"marching cubes with iso_level {iso_level}")
    vertices, triangles = mcubes.marching_cubes(data, iso_level)
    print("finished marching cubes")

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
        img = cv2.resize(img, None, fx=FLAGS.RES_MULT, fy=FLAGS.RES_MULT)
        # img = img.astype(np.float32)
        # img = (img - 127.0) / 255.0
        all_images.append(img)
    return np.array(all_images)


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

    print("Done !")


if __name__ == "__main__":
    app.run(main)
