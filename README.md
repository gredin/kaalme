# kaalme

Ce script coupe le son du générique dans les épisodes de Kaamelott.

Son intérêt est de préserver ma santé mentale lorsque je veux regarder un grand nombre de ces épisodes à la suite. 

Il repose sur la corrélation croisée ([_cross-correlation_](https://en.wikipedia.org/wiki/Cross-correlation)) du son d'un épisode avec un extrait du générique, afin d'identifier à quel instant le générique commence.

## Prérequis

- Python 3 (testé avec la version _3.6.6_)
- ffmpeg (testé avec la version _3.4.3-1_)

## Utilisation

    virtualenv -p /usr/bin/python3 env
    source env/bin/activate
    pip install -r requirements.txt

Il suffit ensuite de fournir le chemin d'accès aux épisodes au format _mkv_.

    ./kaalme.py ~/Kaamelott/Livre\ I/Épisodes/*.mkv

Les épisodes dont le son du générique est désormais coupé sont alors disponibles dans le dossier `episodes_edited`.

## References

https://en.wikipedia.org/wiki/Cross_correlation
https://en.wikipedia.org/wiki/Convolution

https://gist.github.com/patrakov/8a8095721ee81d49f16c

https://stackoverflow.com/questions/33383650/using-cross-correlation-to-detect-an-audio-signal-within-another-signal
https://stackoverflow.com/questions/5847570/use-convolution-to-find-a-reference-audio-sample-in-a-continuous-stream-of-sound
https://stackoverflow.com/questions/5843713/find-audio-sample-in-audio-file-spectrogram-already-exists
https://dsp.stackexchange.com/questions/1370/find-similar-music-using-fft-spectrums/1383#1383
https://dsp.stackexchange.com/questions/2556/audio-signal-comparison-for-automatic-singing-evaluation/2559#2559
