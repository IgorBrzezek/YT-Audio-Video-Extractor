# YouTube Audio & Video Extractor (v1.12)

**Author:** Igor Brzezek (igor.brzezek@gmail.com)
**GitHub:** https://github.com/IgorBrzezek/yt-audio-download
**Version:** 1.12

---

## 1. OPIS

Jest to skrypt Pythona działający w linii poleceń, przeznaczony do pobierania treści z YouTube. Działa jako zaawansowana i przyjazna dla użytkownika nakładka na narzędzia `yt-dlp` i `ffmpeg`.

Jego głównym celem jest:
a) Wyodrębnienie dźwięku najwyższej jakości, konwersja do MP3 i zapisanie go.
b) Pobranie pełnego wideo (z dźwiękiem) w najlepszej dostępnej jakości i zapisanie go jako plik MP4.

Skrypt jest zaprojektowany pod kątem niezawodności, obsługując pojedyncze linki lub duże partie linków z pliku. Zawiera kluczowe funkcje do omijania typowych błędów pobierania z YouTube, ograniczania prędkości i restrykcji, takie jak używanie plików cookie przeglądarki. Oferuje różne tryby wyświetlania informacji: od szczegółowych pasków postępu, przez minimalistyczny status w jednej linii, aż po całkowicie cichą pracę dla zadań wsadowych.

---

## 2. WYMAGANIA

Przed uruchomieniem skryptu **MUSISZ** mieć zainstalowane następujące narzędzia, dostępne z linii poleceń systemu (tj. dodane do systemowej zmiennej środowiskowej PATH):

1.  **Python 3:**
    * Skrypt jest napisany w Pythonie 3.
    * Potrzebna będzie również biblioteka `colorama`:
        ```bash
        pip install colorama
        ```

2.  **yt-dlp:**
    * Jest to główny silnik pobierania.
    * Pobierz stąd: [https://github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)
    * **KRYTYCZNE:** YouTube często zmienia swoją stronę. MUSISZ utrzymywać `yt-dlp` w aktualnej wersji.
        Uruchamiaj tę komendę regularnie:
        ```bash
        yt-dlp -U
        ```

3.  **ffmpeg & ffprobe:**
    * Są wymagane do ekstrakcji audio i łączenia plików MP4.
    * Pobierz stąd: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
    * Skrypt zakończy się błędem, jeśli nie będzie mógł wywołać `ffmpeg` i `ffprobe` z terminala.

---

## 3. UŻYCIE

Podstawowa składnia linii poleceń:

# Dla jednego lub więcej URL-i
python yt_extractor.py [OPCJE] "URL_1" "URL_2" ...

# Do przetwarzania wsadowego z pliku
python yt_extractor.py --list "moje_linki.txt" [OPCJE]
WAŻNE: Zawsze umieszczaj adresy URL w podwójnych cudzysłowach (" "). Zapobiega to błędnej interpretacji przez wiersz poleceń znaków specjalnych, takich jak & (często występujący w adresach URL playlist YouTube).

## 4. SZCZEGÓŁOWY OPIS OPCJI

Poniżej znajduje się opis wszystkich dostępnych opcji linii poleceń, pogrupowanych według kategorii.

Opcje Pomocy
-h, --short-help Pokazuje krótką, jednolinijkową pomoc dla najczęstszych poleceń.

--help Pokazuje pełną, szczegółową pomoc (tę samą, która znajduje się w nagłówku skryptu).

Opcje Wejścia i Wyjścia
urls (Pozycyjny) Jeden lub więcej adresów URL wideo YouTube, oddzielonych spacjami. Ten argument jest ignorowany, jeśli użyto opcji --list. Przykład: python yt_extractor.py "URL1" "URL2"

-o FILENAME, --output FILENAME Określa niestandardową nazwę pliku wyjściowego. WAŻNE: Ta opcja działa TYLKO podczas pobierania JEDNEGO adresu URL. Zostanie zignorowana, jeśli podasz wiele adresów URL lub użyjesz listy. Przykład: -o "Moja Nazwa Pliku.mp3"

--list FILE Ścieżka do pliku tekstowego zawierającego listę adresów URL do przetworzenia. Plik powinien zawierać jeden adres URL w każdej linii. NIE używaj cudzysłowów wokół adresów URL wewnątrz pliku. Przykład: --list "linki.txt"

-dst DIRECTORY Określa katalog docelowy, w którym zostaną zapisane wszystkie pobrane pliki. Jeśli nie zostanie podany, pliki są zapisywane w tym samym katalogu co skrypt. Przykład: -dst "C:\Moja Muzyka\Pobrane"

--overwrite Wymusza nadpisanie istniejących plików. Przekazuje flagę --force-overwrite do yt-dlp, zapewniając ponowne pobranie i nadpisanie plików. Ta opcja jest automatycznie włączana podczas używania trybu wsadowego (-b).

Opcje Formatu (Wybierz jedną)
-mp3fast (Domyślna) Jest to tryb domyślny. Pobiera najlepszy dostępny strumień audio i używa ffmpeg do konwersji na wysokiej jakości MP3 VBR (Variable Bitrate). Zapewnia doskonałą jakość i jest bardzo szybki.

-mp3128 Pobiera najlepsze audio i ponownie koduje je jako MP3 CBR (Constant Bitrate) 128 kbps. Użyj tej opcji, jeśli rozmiar pliku jest głównym problemem.

-mp4fast Pobiera pełne wideo. Znajduje najlepszy dostępny strumień wideo i najlepszy dostępny strumień audio, a następnie remuksuje (łączy) je w pojedynczy plik .mp4 bez ponownego kodowania. Najszybszy sposób na pobranie pliku wideo.

Opcje Antyblokujące i Sieciowe
--cookies BROWSER Jest to najskuteczniejsza metoda omijania błędów YouTube, błędów "403 Forbidden", ograniczeń wiekowych i ograniczania prędkości. Informuje yt-dlp, aby użył plików cookie z Twojej zalogowanej przeglądarki.

BROWSER może być: chrome, firefox, edge, brave, opera, safari itp.

Dla zaawansowanych użytkowników z wieloma profilami przeglądarki, można określić jeden, np. --cookies "firefox:default-release" Przykład: --cookies chrome

-r RATE, --limit-rate RATE Ogranicza maksymalną prędkość pobierania. Przydatne, aby uniknąć wykrycia lub przeciążenia połączenia internetowego. Przykład: -r 500K (dla 500 KB/s), -r 2M (dla 2 MB/s)

--add-header Dodaje standardowy nagłówek "User-Agent" przeglądarki do żądania pobierania. Spróbuj tej opcji, jeśli standardowe pobieranie zawiedzie. Nie używaj jednocześnie z --add-android.

--add-android Informuje yt-dlp, aby naśladował żądanie z oficjalnej aplikacji YouTube na Androida. Często skuteczny w omijaniu ograniczeń. Nie używaj jednocześnie z --add-header.

Opcje Trybu Wyświetlania (Wybierz jedną)
(Domyślny) Normalny tryb wyjścia. Pokazuje niezbędne komunikaty, postęp pobierania ([download] ...%) i postęp konwersji (Converting to mp3: ...%). Nie pokazuje szczegółowych komunikatów [youtube] ani [info].

--pb Podobny do trybu domyślnego, ale stara się pokazać bardziej szczegółowy pasek postępu yt-dlp, jeśli to możliwe (rozmiar, prędkość, ETA).

--min Tryb minimalny. Wyświetla tylko jedną, dynamicznie aktualizowaną linię na plik, pokazującą bieżący status (np. Downloading, Converting) i procenty. Kończy się linią podsumowania dla każdego pliku (czasy, rozmiar).

-b, --batch Tryb cichy (wsadowy). Nie generuje żadnych danych wyjściowych na konsoli (logowanie nadal działa). Automatycznie włącza --overwrite. Idealny do skryptów. Skrypt zwraca kod wyjścia: 0 dla pełnego sukcesu lub N (N > 0) wskazujące liczbę plików, które zawiodły.

Opcje Narzędziowe
--color Wymusza kolorowe wyjście w terminalu (przydatne, jeśli nie jest domyślnie włączone). Ta opcja jest ignorowana w trybach --batch i --min.

--log [FILENAME] Tworzy plik dziennika (domyślnie: yt-dlp.log) w katalogu skryptu. Wszystkie dane wyjściowe, w tym błędy i informacje debugowania (jeśli włączone), zostaną zapisane w tym pliku. Przykład: --log moj_log_pobierania.txt

--debug Włącza tryb szczegółowy (verbose). Drukuje wszystkie surowe, szczegółowe dane wyjściowe z poleceń yt-dlp i ffmpeg. Niezbędne do rozwiązywania problemów. Ta opcja jest ignorowana w trybach --batch i --min.

## 5. PRZYKŁADY

Oto 10 przykładów obejmujących różne scenariusze.

Przykład 1: Podstawowe pobieranie audio (Domyślne) Pobiera pojedynczy utwór jako wysokiej jakości plik MP3 przy użyciu ustawień domyślnych.

python yt_extractor.py "[https://www.youtube.com/watch?v=dQw4w9WgXcQ](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
Przykład 2: Pobieranie pełnego wideo (Najszybsze) Pobiera najlepsze wideo i audio, szybko łącząc je w plik MP4.

python yt_extractor.py -mp4fast "[https://www.youtube.com/watch?v=VIDEO_ID_HERE](https://www.youtube.com/watch?v=VIDEO_ID_HERE)"
Przykład 3: Zalecane "bezpieczne" pobieranie (Używanie plików cookie) Najlepsza metoda unikania większości błędów (403, ograniczenia wiekowe). Używa plików cookie Chrome.

python yt_extractor.py --cookies chrome "[https://www.youtube.com/watch?v=AGE_RESTRICTED_ID](https://www.youtube.com/watch?v=AGE_RESTRICTED_ID)"

Przykład 4: Przetwarzanie wsadowe listy do określonego folderu Pobiera wszystkie adresy URL z "moja_playlista.txt" jako domyślne pliki MP3 do folderu "Moja Muzyka".

python yt_extractor.py --list "moja_playlista.txt" -dst "C:\Users\MojUzytkownik\Music"
Przykład 5: Wiele adresów URL, mniejszy rozmiar pliku (128kbps MP3) Pobiera dwa określone adresy URL jako mniejsze pliki MP3 128 kbps i umieszcza je w podfolderze "Podcasty".

python yt_extractor.py -mp3128 -dst "./Podcasty" "URL_1" "URL_2"
Przykład 6: Niestandardowa nazwa pliku i wymuszone nadpisanie Pobiera pojedyncze wideo jako MP4, nazywa je "MojeWideo.mp4" i wymusza nadpisanie, jeśli już istnieje.

python yt_extractor.py -mp4fast -o "MojeWideo.mp4" --overwrite "URL_VIDEO"
Przykład 7: Minimalny postęp dla listy Pobiera wszystkie adresy URL z "linki.txt" jako domyślne pliki MP3, pokazując tylko jednolinijkowe minimalne aktualizacje postępu.

python yt_extractor.py --list "linki.txt" --min
Przykład 8: Cicha praca wsadowa z logowaniem Pobiera adresy URL z "lista_pracy.txt" całkowicie cicho (-b), zapisując wszystkie logi do "log_pracy.txt". Sprawdź kod wyjścia systemu po zakończeniu, aby zobaczyć liczbę błędów.

python yt_extractor.py --list "lista_pracy.txt" -b --log "log_pracy.txt"

# W systemie Linux/macOS: echo $?

# W systemie Windows: echo %ERRORLEVEL%

Przykład 9: Alternatywna strategia z ograniczeniem prędkości Jeśli standardowe pobieranie zawiedzie, spróbuj użyć symulacji klienta Android i ogranicz prędkość do 1 MB/s, aby wyglądać mniej agresywnie.

python yt_extractor.py --add-android -r 1M "[https://www.youtube.com/watch?v=STUBBORN_ID](https://www.youtube.com/watch?v=STUBBORN_ID)"
Przykład 10: Pobieranie audio z określoną nazwą wyjściową i debugowaniem Pobiera pojedynczy plik audio, nadaje mu konkretną nazwę, włącza kolory i pokazuje wszystkie szczegółowe dane wyjściowe debugowania z yt-dlp/ffmpeg.

python yt_extractor.py -o "KonkretnyUtwor.mp3" --color --debug "URL_SONG"

## 6. ROZWIĄZYWANIE PROBLEMÓW I NAJLEPSZE PRAKTYKI

"ERROR: ... 403: Forbidden" lub "Age-Restricted"

Rozwiązanie: Użyj opcji --cookies BROWSER. Rozwiązuje to problem w 99% przypadków.

Skrypt zawodzi przy WSZYSTKICH pobraniach (nawet prostych)

Rozwiązanie: Twoje yt-dlp jest przestarzałe. YouTube zmienia kod swojej strony, a yt-dlp musi być zaktualizowane, aby pasowało. Uruchom yt-dlp -U w linii poleceń. Rób to regularnie.

"ffmpeg: command not found" lub "ffprobe: command not found"

Rozwiązanie: ffmpeg i ffprobe nie znajdują się w systemowej zmiennej PATH. Musisz je pobrać z ffmpeg.org i umieścić w katalogu, który znajduje się w Twojej zmiennej PATH, lub dodać ich lokalizację do zmiennej środowiskowej PATH.

Adresy URL z & (jak playlisty) powodują błędy!

Rozwiązanie: Zapomniałeś umieścić URL w podwójnych cudzysłowach (" "). NIEPOPRAWNIE: python yt_extractor.py https://...&list=... POPRAWNIE: python yt_extractor.py "https://...&list=..."

Wideo nadal się nie pobiera, nawet z plikami cookie.

Rozwiązanie: Wypróbuj alternatywne strategie pobierania: --add-header lub --add-android. Używaj tylko jednej z nich na raz.

Nadpisywanie (--overwrite) wydaje się nie działać.

Rozwiązanie: Upewnij się, że używasz flagi --overwrite. Przekazuje ona --force-overwrite do yt-dlp. Sprawdź, czy nie ma literówek. Tryb wsadowy (-b) automatycznie włącza tę opcję.

## 7. LICENCJA

MIT License