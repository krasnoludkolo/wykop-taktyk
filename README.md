# wykop-taktyk

Bot mający na celu dodanie możliwości obserwowania wspisów w serwisie www.wykop.pl

Idea:
Możwliwość zawołania konta bota (`@taktyk-bot`) aby obserwował wpis i wysyłał PW z informacją o nowych komentarzach.

## Jak używać

### Jak zacząć obserwować wpis?

* jako komentarz pod wpisem na mirko
    * `@taktyk-bot <cokolwiek> ` - rozpoczyna obserwacje wpisu
    * `@taktyk-bot op ` - rozpoczyna obserwacje tylko komentarzy OPa
* wiadomość PW do `@taktyk-bot`
    * `https://www.wykop.pl/wpis/55010593/taktyk-bot-apitest/` - rozpoczyna obserwacje wpisu z linku
    * `55010593` - rozpoczyna obserwacje wpisu o takim id

### Jak przestać obserwować wpis?

* wiadomość PW do `@taktyk-bot`
    * `https://www.wykop.pl/wpis/55010593/taktyk-bot-apitest/` - przestaje obserować wpisu z linku jeśli był
      zaobserowany
    * `55010593` - przestaje obserwować wpisu o takim id jeśli był zaobserowany
