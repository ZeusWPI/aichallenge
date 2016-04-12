{% extends 'markdown.html' -%}
{% set active_page = 'rules' -%}


{% block markdown_content -%}

# Rules (in Dutch)

Wanneer de oude vorst sterft zonder duidelijke erfgenaam, is het land in chaos.
Velen wagen een worp naar de troon, maar slechts enkele maken een kans.
Hiervoor moeten ze echter razendsnel beslissingen nemen, dus is er geen tijd om
te wachten op het besluit van hun raadsheren. Gelukkig zijn enkele van de
strijders om de troon goed gemoderniseerd, en beseffen dat niets zo snel
beslissingen kan nemen als een stevig doordachte Artificiële Intelligentie.
Help jouw vorst met het bouwen van een bot om het land te veroveren!

## Het spelbord

Het spelbord bestaat uit een aantal forten/steden op een landkaart, verbonden
door wegen.

Elke stad wordt gekenmerkt door zijn naam en locatie (x- en y-coordinaat).
Verder heeft een fort één bezetter (jij of één van je tegenstanders) of is het
neutraal, en bevinden zich er een aantal soldaten.

Elke weg loopt in een rechte lijn tussen twee steden, en kan uiteraard gebruikt
worden voor de verplaatsing van soldaten. Eénrichtingsverkeer deed men in de
middeleeuwen nog niet aan mee, dus troepen kunnen zich telkens in beide
richtingen verplaatsen.

Elke speler begint als eigenaar van 1 fort met daarin 100 soldaten.

## Het speldoel

Het doel van het spel is eenvoudig: verover het land. Dit doe je door alle
steden te veroveren en alle vijandige troepen uit de weg te ruimen.

## Het spelverloop

Het spel verloopt in beurten, bestaande uit volgende eenvoudige stappen:

- Iedere speler krijgt de staat van het spel meegedeeld. Deze bestaat uit alle
  tegenstanders, forten, wegen en troepen die hij kan zien (zie "Fog of war").
- Na zorgvuldige analyse en goed nadenken deelt elke speler zijn commando's
  mee. Er is slechts één vorm van commando's: MARCHEREN! Elke speler zal dus
  elke beurt troepen op pad kunnen sturen uit steden die hij bezet heeft.
- Als alle commando's meegedeeld zijn, zal het spel alle troepen verplaatsen en
  conflicten (veldslagen) verwerken.
- Na het verwerken van de conflicten zal in elk bezet fort een rekrutering
  plaatsvinden, waardoor het aantal soldaten daar groeit. Dit resulteert in een
  nieuwe configuratie van het spelbord, welke in volgende beurt aan de speler
  wordt meegedeeld.

Het verplaatsen van troepen is eenvoudig: elke beurt zet elk leger een "stap"
verder in de richting waarin het loopt. Komt het daardoor toe in een fort,
vindt er een belegering plaats. Komt het een ander (vijandig) leger tegen
onderweg, krijgt men een veldslag. In de andere gevallen wordt gewoon de
afstand afgelegd.

### Veldslagen

Wanneer twee vijandige legers elkaar kruisen, vindt er een veldslag plaats. Van
beide legers wordt de grootte vergeleken. Zijn beide legers even groot, zullen
ze elkaar tot op de laatste man afslachten, en eindigt het verhaal voor beide.
Als één van de twee legers groter is, zal dat leger overwinnen. Het kleinere
leger wordt uit het spel verwijderd, nadat zijn grootte van het grotere leger
afgetrokken werd. Elke soldaat neemt als het ware één vijand mee de dood in.

Na de veldslag zal het overlevende leger zijn reis verderzetten in dezelfde
richting.

### Belegeringen

Een belegering wordt op gelijkaardige manier afgehandeld als een veldslag, met
het verschil dat er meerdere legers (waaronder mogelijks versterkingen)
tegelijk kunnen toekomen bij een fort. Om het spel eenvoudig te houden worden
eerst alle versterkingen binnen in het kasteel gelaten, en laten we de troepen
van verschillende belegeraars samenkomen. We krijgen dus 1 leger per speler
aanwezig.

Vervolgens kijken we welke speler het kleinste aantal soldaten heeft. Dit leger
wordt uitgeschakeld, en net als bij een veldslag wordt van elke tegenstander de
grootte van dit leger afgetrokken. Dit herhalen we tot er één of geen (bij
gelijke legers) spelers over zijn.

Is er juist één speler over, wordt dit de nieuwe eigenaar van het fort. De
overschot van zijn troepen marcheert het kasteel binnen. Zijn de grootste
legers juist evengroot, waardoor er geen overwinnaar in leven lijft, wordt het
fort door zijn vorige eigenaar behouden, zelfs al had deze het minste troepen.
Het kasteel is echter helemaal leeg, en zal pas op het einde van de beurt terug
gevuld raken met enkele rekruten.

### Fog of war

Om het spel wat spannend te houden, spelen we met incomplete informatie. Net
als in echte oorlogen (voor het tijdperk van google maps, althans) moet je
verkenners uitsturen om het terrein voor jou te verkennen. Deze kunnen helaas
niet voorbij vijandige steden sluipen. Als de status van het spel aan jou
verteld wordt, zal deze dus beperkt zijn tot volgende informatie:

- De locatie en naam van alle forten waarvan jij de eigenaar bent.
- De locatie, naam, eigenaar en troepenaantal van elke stad die rechtstreeks
  met één van jouw forten verbonden is.
- Elke weg die vertrekt in één van jouw steden en alle troepen die zich erop
  bevinden.

Merk op dat je informatie kan verliezen als je steden verliest! Hou dus zeker
in je eigen bot alle vergaarde kennis goed bij.

## Formaten

In het spel worden twee formaten gebruikt: één om het speelveld te beschrijven,
zoals het meegedeeld wordt aan de spelers, en één om de commando's van de
spelers door te geven aan het spel. Om alles eenvoudig te houden, zijn dit
gewoon *plain text* bestanden.

### <a name="formaat-speelveld">Formaat speelveld</a>

Hieronder een voorbeeld van een spelconfiguratie.

    3 forts:
    boyard 10 20 felix 100
    helsingor 20 10 ilion 200
    nox 30 30 neutral 0
    2 roads:
    boyard helsingor
    helsingor nox
    2 marches:
    boyard helsingor felix 100 2
    helsingor boyard ilion 10 3

We zien 3 secties in het formaat: eerst komen de forten, dan de straten, en
tenslotte de marcherende legers. Elke sectie begint met een titel, waarin staat
hoeveel elementen de sectie bevat. Elk element bestaat uit één regel:

- Een fort wordt omschreven door zijn naam (bijvoorbeeld, "boyard"), zijn
  coördinaat (2 gehele getallen, eerst x, dan y), zijn eigenaar (bijvoorbeeld
  "ilion") of "neutral" in het geval het fort geen eigenaar heeft, en tenslotte
  het aantal soldaten (tevens een geheel getal).
- Een straat wordt eenvoudigweg omschreven door de namen van de twee steden die
  het verbind.
- Een marcherend leger wordt omschreven door 2 steden (eerst de stad waaruit
  het vertrekt, dan de stad waar het naar toe gaat), de eigenaar van het leger,
  het aantal soldaten waaruit het bestaat, en tenslotte binnen hoeveel beurten
  het leger op zijn bestemming zal toekomen.

### <a name="formaat-commandos">Formaat commando's</a>

Het formaat van een commando lijkt erg op dat van een marcherende troep:

    2 commands:
    boyard helsingor 100
    helsingor boyard 10

Bovenstaand commando's zullen bijvoorbeeld 100 soldaten uit boyard naar
helsingor laten marcheren, en 10 soldaten uit helsingor naar boyard verzenden.

## Speleinde

Het spel eindigt, zoals eerder vermeld, als er 1 speler alle forten veroverd
heeft, en alle troepen van de tegenstander uitgeschakeld heeft. Als er na 500
stappen nog geen winnaar is, eindigt het spel in gelijkstand.


# Getting started

Een bot schrijven is op zich triviaal. Het is niet meer dan een programma
schrijven (in eender welke programmeertaal) die informatie zoals [hierboven
beschreven](#formaat-speelveld) inleest via standaard invoer, en die commando's
stuurt zoals [hierboven beschreven](#formaat-commandos) schrijft naar standaard
uitvoer. We zullen je bot oproepen met één argument: de naam die we toekennen
aan je bot. Op die manier weet je welke forten van jou zijn.

Mocht dit niet duidelijk zijn, kan je altijd eens kijken naar de voorbeeld-bots
op [de GitHub
repo](https://github.com/ZeusWPI/aichallenge/tree/master/battlebots/testbots).

## Op je eigen computer testen

Stel dat je nu een dergelijk programma hebt geschreven, bijvoorbeeld genaamd
`bot.py`, dan willen we deze natuurlijk testen door deze te laten vechten tegen
andere bots of tegen zichzelf. Hiervoor schrijven we eerste een klein
configuratie-bestandje in JSON, bijvoorbeeld `config.json`:

    {
        "players": {
            "bot1": "python bot.py",
            "bot2": "python bot.py"
        },
        "mapfile": "test.input",
        "logfile": "sample.data",
        "max_steps": 500
    }

Wanneer we dit configuratiebestandje meegeven aan de arbiter, zullen twee
versies van `bot.py` tegen elkaar vechten op het speelveld van `test.input`.
Deze zal een verslag van het gevecht uitschrijven in `sample.data`.
De arbiter is een Python 3.5 programma dat in [de GitHub
repo](https://github.com/ZeusWPI/aichallenge) staat, dus clone eerst deze repo
en roep dit programma als volgt met je zonet geschreven configuratiebestand als
argument:

    python3 arbiter/arbiter.py config.json

Vervolgens kunnen we dit verslag gebruiken om het verloop van het gevecht te
visualisueren. Open het HTML-bestand `visualize/visualize.html` van deze repo in
je browser en selecteer `sample.data`.

## Laten vechten tegen andere bots

Als je een ietwat werkende bot hebt, kan je deze laten vechten tegen bots van
andere deelnemers. [Maak een account aan]({{ url_for('register') }}) op deze
site, laad je bot op en er zullen automatisch gevechten met je bot worden
uitgevoerd. Hoe meer matches gespeeld, hoe meer je rangschikking ten opzichte
van de andere bots convergeert.

Zo, nu je weet hoe je bot kan testen, ben je klaar om wicked bots te beginnen
schrijven!

{%- endblock %}
