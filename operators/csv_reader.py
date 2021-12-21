from csv import reader
from pathlib import Path


class Reader:
    @staticmethod
    def csv_to_masks(csv_names) -> dict:
        """ Return a list of masks with csv file name
        """
        masks = {}
        for cn in csv_names:
            csv_path = str(Path(__file__).parent) + "/tables/" + cn + ".csv"
            with open(csv_path, 'r') as read_mask:
                masks[cn] = list(reader(read_mask))
                masks[cn] = [[float(i) for i in row] for row in masks[cn]]
        return masks
