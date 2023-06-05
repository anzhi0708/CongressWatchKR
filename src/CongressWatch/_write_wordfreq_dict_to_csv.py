import pickle
import csv


for nth in range(18, 21):
    filename = f"top20_{nth}th_TupleOfTwoDicts_akaWordFreq.pickle"
    with open(filename, 'rb') as bin:
        tup = pickle.load(bin)
        male = tup[0]
        female = tup[1]
        csv_filename_m = filename.replace(".pickle", "_male.csv")
        csv_filename_f = filename.replace(".pickle", "_female.csv")
        with open(csv_filename_m, 'w') as csv_out:
            writer = csv.writer(csv_out)
            writer.writerow(["word", "count"])  # header
            for k in male:
                writer.writerow([k, male[k]])
        with open(csv_filename_f, 'w') as csv_out:
            writer = csv.writer(csv_out)
            writer.writerow(["word", "count"])  # header
            for k in female:
                writer.writerow([k, female[k]])
