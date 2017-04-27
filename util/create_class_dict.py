# Creates maps from integers to class labels and vice versa
import pickle
import pprint
import os

txt_path = '/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data'

int_to_labels = {}
labels_to_int = {}
i = 0
with open(os.path.join(txt_path, 'imagenet_classes.txt')) as f:
        label = f.readline().strip()
        while i < 1000:
            if i < 10:
                print(label)
            if label in labels_to_int:
                print("Duplicate label: {}".format(label))
            labels_to_int[label] = i
            int_to_labels[i] = label
            if i == 10:
                pprint.pprint(int_to_labels)
                pprint.pprint(labels_to_int)
            if i == 999:
                pprint.pprint(int_to_labels[999])
            label = f.readline().strip()
            i += 1
key_check = len(list(int_to_labels.keys()))
key_check2 = len(list(labels_to_int.keys()))
print("{} keys in int to labels, {} keys in labels to int".format(key_check, key_check2))
pickle.dump(int_to_labels, open('int_to_labels.p', 'wb'))
pickle.dump(labels_to_int, open('labels_to_int.p', 'wb'))
print("Label maps saved")

