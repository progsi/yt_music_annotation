import os
import pandas as pd
from datetime import datetime
import ast


def main():

    annotated = pd.DataFrame([], columns=['example', 'changed', 'label', 'annotator', 'timestamp', 'duration'])

    print(f"{len(file_list)} annotation files")

    for filename in file_list:
        try:
            read_df = pd.read_csv(os.sep.join(
                (ANNOTATED_PATH, filename)),
                sep=';',
                dtype={
                    'example': str,
                    'changed': bool,
                    'label': str,
                    'annotator': str,
                    'timestamp': object
                },
                parse_dates=["timestamp"],
                infer_datetime_format=True)
        except UnicodeDecodeError:
            print(f"Error for {filename}")

        read_df['duration'] = read_df['timestamp'].diff().apply(lambda x: x.total_seconds())
        annotated = pd.concat([annotated, read_df])  # .reset_index(drop=True)

    print(f"Length before deduplication {len(annotated)}")

    # drop duplicates in cases of multiple annotations by one annotator and keep last annotated
    annotated.sort_values(by='timestamp', inplace=True)
    annotated.drop_duplicates(subset=['example', 'annotator'], keep='last', inplace=True)

    print(f"Length after deduplication {len(annotated)}")

    annotated['anchor_yt_url'] = annotated['example'].apply(
        lambda x: f'https://www.youtube.com/watch?v={ast.literal_eval(x)[0]}')
    annotated['candidate_yt_url'] = annotated['example'].apply(
        lambda x: f'https://www.youtube.com/watch?v={ast.literal_eval(x)[1]}')
    annotated['anchor_yt_id'] = annotated['example'].apply(lambda x: ast.literal_eval(x)[0])
    annotated['candidate_yt_id'] = annotated['example'].apply(lambda x: ast.literal_eval(x)[1])

    # remove annotator SH, because messy experimental data
    annotated = annotated.loc[annotated.annotator != 'SH', :]

    # fill false to non video
    annotated["with_video"].fillna(value=False, inplace=True)

    annotated.to_csv('annotated.csv', sep=';')

    cross_validated = annotated.groupby(
        by=['example'], as_index=False).filter(
        lambda x: (x['annotator'].count() == len(annotated['annotator'].unique())).all())['example']

    # everything that is already cross-validated (more than 2 evaluators)
    annotated_crossval = annotated.apply(lambda x: x.example in cross_validated, axis=1)

    # write a file for each annotator
    for annotator in annotated['annotator'].unique():
        to_crossval = annotated.loc[(~annotated.example.isin(cross_validated)) & (annotated.annotator != annotator), ['anchor_yt_id', 'candidate_yt_id']]
        to_crossval.columns = ['query_id', 'candidate_id']
        to_crossval['set_id'] = -1
        to_crossval = to_crossval[['set_id', 'query_id', 'candidate_id']]
        to_crossval.to_csv(f'eval_input_crossval_{annotator}.csv', index=False, sep=';')


if __name__ == "__main__":
    # read annotated files

    ANNOTATED_PATH = 'annotated/'

    file_list = os.listdir(ANNOTATED_PATH)

    main()
