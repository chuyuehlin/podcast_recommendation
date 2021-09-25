echo 0to2
tar -xf podcasts-transcripts-0to2.tar.gz spotify-podcasts-2020
python3 data_transform.py
rm -r -f spotify-podcasts-2020

echo 3to5
tar -xf podcasts-transcripts-3to5.tar.gz spotify-podcasts-2020
python3 data_transform.py
rm -r -f spotify-podcasts-2020

echo 6to7
tar -xf podcasts-transcripts-6to7.tar.gz spotify-podcasts-2020
python3 data_transform.py
rm -r -f spotify-podcasts-2020
