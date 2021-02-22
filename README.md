# wykop-taktyk

Bot mający na celu dodanie możliwości obserwowania wpisów w serwisie www.wykop.pl

Idea:
Możliwość zawołania konta bota (`@taktyk-bot`), aby obserwował wpis i wysyłał PW z informacją o nowych komentarzach.

## Jak używać

### Jak zacząć obserwować wpis?

* jako komentarz pod wpisem na mirko
    * `@taktyk-bot <cokolwiek> ` - rozpoczyna obserwacje wpisu
    * `@taktyk-bot op ` - rozpoczyna obserwacje tylko komentarzy OPa

### Jak przestać obserwować wpis?

* wiadomość PW do `@taktyk-bot`
    * `https://www.wykop.pl/wpis/55010593/taktyk-bot-apitest/` - przestaje obserwować wpisu z linku jeśli był
      zaobserwowany
    * `55010593` - przestaje obserwować wpisu o takim id jeśli był zaobserowany
