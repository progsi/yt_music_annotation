import seaborn as sns
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def pivot_annotations():
    annotated_pivot = annotated[['anchor_yt_id', 'candidate_yt_id', 'label', 'annotator']].pivot(
        index=['anchor_yt_id', 'candidate_yt_id'],
        columns=['annotator'],
        values=['label']
    ).reset_index().dropna()
    annotated_pivot['agreement'] = annotated_pivot[('label', 'AE')] == annotated_pivot[('label', 'AS')]
    return annotated_pivot


def get_agreement_dataset():
    data = pivot_annotations()
    data.columns = ['A_yt_id', 'B_yt_id', 'label', 'label2', 'agreement']
    return data.loc[data.agreement, ['A_yt_id', 'B_yt_id', 'label']]


def label_distribution_plot(data: pd.DataFrame, agreed=False):
    sns.color_palette("crest", as_cmap=True)

    if agreed:
        plt.title('Distribution of agreed annotations')
        sns.countplot(data=data, x=data.label, palette='crest')

    else:
        plt.title('Distribution of all annotations')
        sns.countplot(data=data, x=data.label, palette='crest', hue='annotator')

    plt.xticks(rotation=45)

    pdf.savefig(dpi=900, bbox_inches='tight')
    plt.close()
    plt.clf()


def time_distribution_plot():
    # remove pairs where annotation was greater than 10mins
    annotated_duration_cleaned_6mins = annotated.loc[annotated.duration < 360, :]

    annotated_duration_cleaned_6mins.duration.hist(bins=100)
    plt.xlabel('duration in seconds')
    plt.ylabel('count')
    plt.title('Limited to 6mins per pair')

    pdf.savefig(dpi=900, bbox_inches='tight')
    plt.close()
    plt.clf()


def agreement_countplot():

    data = pivot_annotations()

    sns.countplot(x=data['agreement'])

    percentages = data['agreement'].value_counts(normalize=True)
    n_agree = round(percentages.loc[True], 2)
    n_disagree = round(percentages.loc[False], 2)

    plt.title(f"Agreement of {n_agree} to {n_disagree}")
    pdf.savefig(dpi=900, bbox_inches='tight')
    plt.close()
    plt.clf()


def main():

    label_distribution_plot(annotated)
    time_distribution_plot()
    agreement_countplot()
    agreement_dataset = get_agreement_dataset()
    label_distribution_plot(agreement_dataset, True)

    agreement_dataset.to_csv('agreed_annotations.csv', sep=';', index=False)


if __name__ == "__main__":
    # read annotated files

    annotated = pd.read_csv('annotated.csv', sep=';')

    pdf = PdfPages("annotation_analysis.pdf")

    main()

    pdf.close()
