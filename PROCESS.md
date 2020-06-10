## Process Book
# for Stadsgids Amsterdam

**20 april 2020**
README.md aangemaakt, gekozen om te werken met de Tripadvisor API, API-key aangevraagd maar het is een beetje vaag op de site aangegeven of ik uberhaupt toegang ga krijgen. Voorwaarden zijn niet heel duidelijk, afwachten dus. Ondertussen gekeken naar de Facebook API om evenementen van locaties te kunnen weergeven op de site maar dit blijkt niet meer mogelijk met de API. Functie valt dus af. Eventueel een extra pagina in dashboard waar de auteur handmatig via een formulier evenementen aan een locatie kan toevoegen.

**27 april 2020**
Tripadvisor API-key aanvraag afgewezen, gelijk google places API-key aangevraagd, is direct binnen. Idee is nu om voor iedere locatie in Amsterdam met gebruik van de API een locatiepagina te genereren. De aanbevolen locaties krijgen een meer prominente plek op de site en verschijnen met een label in de zoekopdrachten.

**4 mei 2020**
Begonnen met design document, alle pagina's geschetst en gekeken welke links waar nodig zijn. Ook verwerkt welke pagina's moeten worden afgeschermd voor niet gebruikers of niet administratos. Voor de verschillende gebruikersrollen wil ik Flask-User gaan gebruiken, uit de documentatie blijkt dat deze extensie dit kan.

**5 mei 2020**
Flask-User is geen vrienden met Flask-Login en Flask-Admin. Flask user gebruikt een paar verschillende functies en deorators met dezelfde naam als Flask-Login waardoor de code erg buggy wordt. Ik heb de tabellen roles en userroles overgenomen van de documentatie en daarbij zelf een role_required decorator geschreven. Hierdoor Flask-User niet meer nodig. Ook de Flask-Admin pagina's zijn afgeschermd met behult van een geschreven class AdminView.

**6 mei 2020**
Formulier validatie toegevoegd, heb ervoor gekozen om deze nog verder uit te breiden dan bij de vorige opdracht. Javascript zorgt er nu voor dat alleen als alle velden correct zijn ingevuld het formulier verzonden wordt. Denk aan een geldige maar ook beschikbare gebruikersnaam en dat de wachtwoorden ook overeenkomen. De validatie werkt nog steeds als javascript uit staat, nadeel is wel dat door het herladen van de pagina dan alle ingevulde velden weer leeg zijn.

**11 mei 2020**
Gewerkt aan design van de persoonlijke indexpagina. Wilde bij de contactpagina bootstrap validator gebruiken voor het contactformulier maar dit bleek niet te werken met mijn andere styling omdat ik bootstrap niet vanaf het begin heb toegevoegd. Heb gekozen om zelf een korte javascript validator te schrijven om dit te kunnen omzeilen.

**12 mei 2020**
Vandaag Flask mail toegevoegd en getest. Werkte na wat aanpassingen in de instellingen soepel met de andere modellen van de applicatie. De verificatiemails en codes die daarbij gebruikt worden hebben een soort van tijdsstempel nodig om na een tijdje ongeldig te worden. Heb de User-tabel aangepast om meer gegevens hierover te kunnen opslaan.

**13 mei 2020**
Verder gekeken naar e-mail bevestigingscodes. Heb op internet URLSafeTimedSerializer van itsdangerous gevonden. Via dit pakket is het gelukt om de bevestigingslink te laten vervallen in 60 minuten.

**14 mei 2020**
Begonnen met het verwerken van de Google Places API in mijn app. Er zijn verschillende API's om locatie te kunnen zoeken met verschillende prijzen. Nu wil ik niet dat later dikke rekeningen op de mat vallen als ik wat meer API verzoeken via de website krijg. Bij de Google Places search API kan ik zelf bepalen welke informatie er wordt geretouneerd, deze is goedkoper naarmate je minder infomatie aanvraagt. Ik kies ervoor om voor de normale zoekopdrachten deze API te gebruiken en om te kiezen voor alle 'basic' informatie. Hier zitten geen extra kosten aan verbonden.

**15 mei 2020**
De Google Places search API retouneerd ook locaties buiten amsterdam, zelfs wanneer je een lengte/breedtegraad en straal opgeeft in de parameters. Het blijkt een voorkeur te zijn voor de zoekopdracht in plaats van een hard filter. Ik kies ervoor om de resultaten van de API te filteren. Ik strip de adressen van komma's en splits ze vervolgens op spaties. Vervolgens voeg ik een conditie in die checkt of "Amsterdam" in de gesplitste lijst aanwezig is om te bepalen of deze mag worden opgenomen in de resultaten.

**16 mei 2020**
Ik zie dat voor het tonen van foto's een andere API van google moet worden geraadpleegt. Deze heeft extra kosten wanneer de aantallen verzoeken oplopen. Omdat ik per locatie een foto wil laten zien bij de resultaten heb ik ervoor gekozen om deze API verzoeken te doen nadat de resultaten, die niet in Amsterdam liggen, gefilterd zijn zodat het aantal verzoeken voor deze API minimaal blijven.

Voor het geavanceerde zoeken ga ik gebruikmaken van de Google nearby search API omdat met deze API ik verschillende zoekfilters kan instellen maar ook omdat je hier in het zoekveld ontelbaar veel verschillende zoektermen kan gebruiken zoals adressen of meer specifieke filters. Het is me wel opgrvallen dat als ik nu zoek met een leeg zoekveld en alleen een typefilter ik veel locaties in de resultaten krijg. Veel resultaten hiertussen zijn zogenoemde "Adult content" of van types die ik niet op mijn site wil weergeven (denk aan pinautomaten, advocatenkantoren etc.). Om dit probleem met deze API, maar ook hetzelfde probleem voor de eerdergenoemde API, op te lossen kies ik ervoor om de resultaten altijd te filteren op een lijst met types die ik wel wil weergeven op de site. Om de "Adult content" van de site te filteren splits en strip ik dit keer de titel in een lijst en filter ik de resultaten op bepaalde kernwoorden in de titel van de locatie.

**17 mei 2020**
Bezig met de locatiepagina en de verschillende functies hierop. Ik wilde eerst dat wanneer iemand aangaf ergens geweest te zijn na een paar dagen een e-mail versturen om de plek een recensie te geven. Dit is alleen niet mogelijk met Flask-mail. Ik heb gekozen om de functionaliteit aan te passen en er een "Is dit wat?" knop van te maken. Klikt de gebruiker op deze knop, dan wordt er een email naar de beheerder gestuurd met informatie over de gebruiker en de locatie zodat de beheerder een email terug kan sturen om deze plek aan te raden of juist af te raden.

**18 mei 2020**
Laatste dag om aan de code te werken, ik heb ervoor gekozen om me echt te focussen op de locatiepagina omdat dat naar mijn mening de belangrijkste pagina is. Ik heb een knop toegevoegd voor de beheerder om de locatie aan te bevelen en om de aanbeveling aan te passen wanneer de pagina al is aanbevolen. Op de pagina voor het aanmaken van de aanbeveling heb ik een checkbox voor de zichtbaarheid toegevoegd. Dit omdat ik me kan voorstellen dat wanneer je een stukje schrijft over de pagina en deze gedurende die sessie niet af kan maken het raar is als er een halve aanbeveling op de website zichtbaar wordt. Als deze checkbox uitstaat wordt de aanbeveling opgeslagen in de database maar niet getoond op de website.

