
# https://data.bris.ac.uk/data/dataset/4vnrca7qw1642qlwxjadp87h7

import glob
import os
import shutil
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

import numpy as np
import supervisely as sly
from dotenv import load_dotenv
from supervisely.io.fs import (
    dir_exists,
    file_exists,
    get_file_ext,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from supervisely.io.json import load_json_file
from tqdm import tqdm

import src.settings as s
from dataset_tools.convert import unpack_if_archive


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count
    
def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:

    # project_name = "Open cows 2021"
    dataset_path = "/home/grokhi/rawdata/cows2021/4vnrca7qw1642qlwxjadp87h7/Sub-levels/Detection_and_localisation"
    batch_size = 30
    ds_name = "ds"
    images_ext = ".jpg"
    ann_ext = ".xml"


    def create_ann(image_path):
        labels = []

        ann_path = os.path.join(images_path, get_file_name(image_path) + ann_ext)

        tree = ET.parse(ann_path)
        root = tree.getroot()
        img_height = int(root.find(".//height").text)
        img_width = int(root.find(".//width").text)
        objects_content = root.findall(".//object")
        for obj_data in objects_content:
            name = obj_data.find(".//name").text
            bndbox = obj_data.find(".//bndbox")
            if bndbox is not None:
                top = int(bndbox.find(".//ymin").text)
                left = int(bndbox.find(".//xmin").text)
                bottom = int(bndbox.find(".//ymax").text)
                right = int(bndbox.find(".//xmax").text)
            else:
                bndbox = obj_data.find(".//robndbox")
                h = int(float(bndbox.find(".//h").text))
                w = int(float(bndbox.find(".//w").text))
                y_center = int(float(bndbox.find(".//cy").text))
                x_center = int(float(bndbox.find(".//cx").text))
                top = y_center - h / 2
                left = x_center - w / 2
                bottom = y_center + h / 2
                right = x_center + w / 2
            if top == bottom or bottom == 0:
                continue
            else:
                rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)
                if rectangle.area > 2400:
                    label = sly.Label(rectangle, obj_class)
                    labels.append(label)
                label = sly.Label(rectangle, obj_class)

            labels.append(label)

        return sly.Annotation(img_size=(img_height, img_width), labels=labels)


    obj_class = sly.ObjClass("cattle torso", sly.Rectangle)
    subfolder_tag = sly.TagMeta("cow_id", sly.TagValueType.ANY_STRING)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(
        obj_classes=[obj_class],
        tag_metas=[subfolder_tag],
    )
    api.project.update_meta(project.id, meta.to_json())

    for ds_name in os.listdir(dataset_path):
        ds_path = os.path.join(dataset_path, ds_name, "images")
        if dir_exists(ds_path):
            if ds_name == "Test":
                dataset = api.dataset.create(
                    project.id,
                    "detection_and_localisation-" + ds_name.lower(),
                    change_name_if_conflict=True,
                )
            for ds_subfolder in os.listdir(ds_path):
                images_path = os.path.join(ds_path, ds_subfolder)
                if dir_exists(images_path):
                    if ds_name != "Test":
                        dataset = api.dataset.create(
                            project.id,
                            "detection_and_localisation-" + ds_subfolder,
                            change_name_if_conflict=True,
                        )
                    images_names = [
                        im_name
                        for im_name in os.listdir(images_path)
                        if get_file_ext(im_name) == images_ext
                    ]

                    progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

                    for img_names_batch in sly.batched(images_names, batch_size=batch_size):
                        images_pathes_batch = [
                            os.path.join(images_path, image_name) for image_name in img_names_batch
                        ]

                        img_infos = api.image.upload_paths(
                            dataset.id, img_names_batch, images_pathes_batch
                        )
                        img_ids = [im_info.id for im_info in img_infos]

                        anns = [create_ann(image_path) for image_path in images_pathes_batch]
                        api.annotation.upload_anns(img_ids, anns)

                        progress.iters_done_report(len(img_names_batch))


    def create_ann_identification(image_path, ds_id):
        labels = []
        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]

        subfolder_value = image_path.split("/")[-3 + ds_id]
        subfolder = sly.Tag(subfolder_tag, value=subfolder_value)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=[subfolder])


    identification_train_path = "/home/grokhi/rawdata/cows2021/4vnrca7qw1642qlwxjadp87h7/Sub-levels/Identification/Train/RGBDCows2020/Identification/RGB"
    identification_test_path = (
        "/home/grokhi/rawdata/cows2021/4vnrca7qw1642qlwxjadp87h7/Sub-levels/Identification/Test"
    )


    for ds_id, identification_path in enumerate([identification_train_path, identification_test_path]):
        if ds_id == 0:
            dataset = api.dataset.create(
                project.id, "identification-train", change_name_if_conflict=True
            )
            images_pathes = glob.glob(identification_path + "/*/*/*.jpg")
        else:
            dataset = api.dataset.create(
                project.id, "identification-test", change_name_if_conflict=True
            )
            images_pathes = glob.glob(identification_path + "/*/*.jpg")

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_pathes))

        for img_pathes_batch in sly.batched(images_pathes, batch_size=batch_size):
            img_names_batch = [
                im_path.split("/")[-3 + ds_id] + "_" + get_file_name_with_ext(im_path)
                for im_path in img_pathes_batch
            ]

            img_infos = api.image.upload_paths(dataset.id, img_names_batch, img_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann_identification(image_path, ds_id) for image_path in img_pathes_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(img_names_batch))
    return project


