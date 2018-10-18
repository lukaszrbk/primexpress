'''
~~~~Primexpress 1.0~~~~


data wydania: 18.10.2018
autor: Łukasz Rybak


Opis:
Program, który w założeniu ma ułatwić pracę specjalistom z zakresu genetyki molekularnej. Automatyzuje wyszukiwanie starterów 
dla sekwencji kodujących dowolnych genów ludzkich (czynność niejednokrotnie wykonywaną podczas codziennej pracy z DNA w laboratoriach 
badawczych i diagnostycznych). Zadanie dotychczas wykonywane godzinami, skraca do rzędu kilku minut i unika przy tym możliwych błędów 
i niedopatrzeń ze strony człowieka. Weryfikacja sekwencji przystosowana dla populacji europejskiej (nie wliczając w to populacji fińskiej.


Strony internetowe, bazy danych i narzędzia użyte w programie:
https://selenium-python.readthedocs.io/installation.html- Selenium for Python - narzędzie do automatyzacji operacji z użyciem stron internetowych
https://primer3plus.com/ - Primer 3 Plus - narzędzie do wyszukiwania primerów (domyślnie używane)
http://primer3.ut.ee/ - Primer 3.0 - narzędzie do wyszukiwania primerów (backup dla Primer 3 Plus)
https://www.lrg-sequence.org/ - Stable reference sequences for reporting variants - baza danych na temat oficjalnego formatu LRG sekwencji genów
https://genome.ucsc.edu/ - Univeristy of California Santa Cruz - baza danych na temat wersji hg19 i hg38 genomu ludzkiego
http://www.ensembl.org/biomart/ - BIOMART- narzędzie do konwersji sekwencji RefSeq (NM_) transkryptu do sekwencji GeneBank (ENST)
http://gnomad-beta.broadinstitute.org/ - GnomAD - baza danych na temat mutacji i zmienności populacyjnych w sekwencji genu


Podstawa teoretyczna:
DNA człowieka składa się z dwóch połączonych ze sobą nici. Podstawowym budulcem każdej z nich są 4 nukleotydy- adenina (A), tymina (T), guanina (G) i cytozyna (C). 
W stanie prawidłowym adenina na jednej z nici łączy się z tyminą na drugiej (i na odwrót), tymczasem cytozyna jest połączona z guaniną. Dodatkowo bardzo istotna jest 
kolejność poszczególnych nukleotydów na nici- tzw. sekwencja. Sekwencję dzielimy między innymi na fragmenty zwane genami, a te z kolei składają się z fragmentów niekodujących 
białek (intronów) i fragmentów odpowiedzialnych za kodowanie białka (eksonów). Zaburzenia w sekwencji nukleotydów (szczególnie w eksonach) prowadzą często do chorób o podłożu 
genetycznym. Dlatego też opracowano technikę sekwencjonowania metodą Sanger'a- reakcję, która pozwala nam 'odczytać' nukleotydy jeden po drugim i w ten sposób stwierdzić nieprawidłowości. 
Nie możemy przy jej użyciu poznać sekwencji całej nici DNA, a jedynie małych jej fragmentów. Fragment, jaki chcemy uzyskać jest ze swojej lewej i prawej strony ograniczony
miejscami startu reakcji sekwencjonowania. Te miejsca startu wyznaczają tzw. primery/startery - kilkunastonukleotydowe fragmenty, które na zasadzie unikalnego dopasowania 
przyłączają się do DNA. Gdy znamy ich sekwencje możemy z łatwością je zsytnetyzować i użyć do reakcji. Sęk w tym, że nie wystarczy po prostu losowo wyznaczyć, jak powinien 
wyglądać primer. Jego sekwencja to składowa mnóstwa zmiennych takich jak temperatura topnienia, określona długość, wzajemna komplementarność i obecność polimorfizmów w łańcuchu. Większość z tych 
parametrów obliczanych jest przez narzędzia bioinformatyczne, takie jak Primer 3.0, czy Primer 3 Plus. Nie są one jednak w stanie same wyznaczyć np. jakiej długości sekwencję trzeba analizować
(zwykle jest to od 300-500pz fragment, a w jego obrębie wyłącznie nukleotydy kodujące białka, wraz z 30pz marginesami), nie mogą samodzielnie wykryć powtarzających się fragmentów (te powodują 
tzw. poślizg polimerazy i zaburzają reakcję), czy możliwych zmienności w nici DNA między ludźmi (niekoniecznie świadczących o mutacjach). Wspomniane zmienności (niebędące patologią)- tzw. polimorfizmy, 
niekiedy są dość częste i  w związku z tym fakt, że zaprojektujemy parę primerów odpowiednią dla jednego Pacjenta nie oznacza, że będzie odpowiednia dla kogoś innego. Program Primexpress bierze 
pod uwagę wszystkie wymienione aspekty i poprzez zautomatyzowanie użycia poszczególnych narzędzi bioinformatycznych i baz danych, w prosty sposób prowadzi do uzyskania sekwencji starterów i niezbędnych
dla specjalisty informacji o niej. Większość wartości parametrów takich jak temperatury i długości łańcuchów, została uzyskana na drodze doświadczalnej przez analizę tysięcy genów na przestrzeni 
lat w medycznym laboratorium diagnostycznym.

----------------------------------------------

Copyright 2018 Łukasz Rybak

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def excluderepetitions (exon):
	'''Powtarzalne nukleotydy mogą zaburzać przebieg reakcji sekwencjonowania. Poniżej funkcja wyłączająca 'nrpt'-razowe powtórzenia nukleotydowe z analizy, za pomocą wstawienia nawiasów <>. W narzędziach typu Primer 3.0 lub Primer 3 Plus jest to oznaczenie regionu niepodlegającego analizie.'''
	exon=exon.replace('a'*nrpt, '<'+'a'*nrpt+'>')
	exon=exon.replace('t'*nrpt, '<'+'t'*nrpt+'>')
	exon=exon.replace('g'*nrpt, '<'+'g'*nrpt+'>')
	exon=exon.replace('c'*nrpt, '<'+'c'*nrpt+'>')
	exon=exon.replace('at'*nrpt, '<'+'at'*nrpt+'>')
	exon=exon.replace('ag'*nrpt, '<'+'ag'*nrpt+'>')
	exon=exon.replace('ac'*nrpt, '<'+'ac'*nrpt+'>')
	exon=exon.replace('tg'*nrpt, '<'+'tg'*nrpt+'>')
	exon=exon.replace('tc'*nrpt, '<'+'tc'*nrpt+'>')
	exon=exon.replace('cg'*nrpt, '<'+'cg'*nrpt+'>')
	if '<' in exon and '>' in exon:
		print('\nProgram dokonał wyłączenia powtórzeń nukleotydowych z zakresu wyszukiwania primerów dla całości lub części EKSONU %s. Zweryfikuj, czy primery nie flankują powtarzalnych fragmentów, co może mieć wpływ na przebieg reakcji sekwencjonowania.\n' %nwsq)
	return exon #zmodyfikowany fragment jest przekazywany dalej do analizy po wcześniejszym poinformowaniu użytkownika o tym fakcie
def primer3search():
	'''Funkcja wyszukująca primery w programie Primer 3.0. Jest to backup dla analogicznej funkcji, wykonywanej przez narzędzie Primer 3 Plus.'''
	driver.get('http://primer3.ut.ee/')
	driver.implicitly_wait(2) #daje czas na załadowanie wszystkich elementów na stronie
	select1=Select(driver.find_element_by_name('PRIMER_MISPRIMING_LIBRARY')) #rozwinięcie listy z kilkoma dostępnymi opcjami
	select1.select_by_visible_text('HUMAN') #wybór primerów dla genomu ludzkiego
	elem15=driver.find_element_by_name('SEQUENCE_TEMPLATE') #wyszukanie okna do wstawienia sekwencji
	elem15.clear()
	elem15.send_keys(prsq) #wprowadzenie sekwencji ze wstawionymi nawiasami klamrowymi
	elem16=driver.find_element_by_name("Pick Primers")
	driver2.move_to_element(elem16).click().perform()
	driver2.reset_actions()
	driver.implicitly_wait(2) #daje czas na załadowanie wszystkich elementów na stronie
	try:
		assert 'NO PRIMERS FOUND' not in driver.page_source, '\nNIE ZNALEZIONO PRIMERÓW DO JEDNEGO Z PODANYCH EKSONÓW (EKSON %s)! WPROWADŹ RĘCZNIE SEKWENCJĘ DO PROGRAMU PRIMER 3.0, ŻEBY SPRAWDZIĆ PRZYCZYNY.\n' % key #sprawdzenie, czy program primer 3.0 nie był w stanie zaprojektować primerów
	except AssertionError as aserr:
		print(aserr) #jeżeli nie można było zaprojektować starterów do jednego z fragmentów, program informuje o tym, ale nie przerywa działania i przechodzi do dalszej analizy reszty eksonów
	else: #zachowanie programu jeżeli primery dla danego eksonu zostały znalezione- lokalizacja elementów bazująca na podobieństwie poszczególnych output'ów 
		elem17=driver.find_element_by_xpath("//pre")
		el17pr=elem17.get_property('textContent')
		ap=el17pr.find('LEFT PRIMER')
		leftprimlen=ap+25 #indeks długości lewego primera zawsze zaczyna się 25 znaków za pierwszą literą łańcucha znaków 'LEFT PRIMER'...
		leftprimlen2=leftprimlen+2 #...i kończy dwie pozycje dalej
		lftlen=el17pr[leftprimlen:leftprimlen2]
		leftprimseq=ap+73 #sekwencja lewego primera zawsze zaczyna się 73 znaki za pierwszą literą łańcucha znaków 'LEFT PRIMER'
		lftprimseqend=int(lftlen)+leftprimseq #do wartości indeksu pierwszej litery sekwencji primera dodajemy długość primera, żeby uzyskać indeks jego prawej granicy
		lprim=(el17pr[leftprimseq:lftprimseqend]).upper() #wycięcie sekwencji primera z elementu '//pre' strony
		print('','#'*50, '\nGEN %s - EKSON %s -- SEKWENCJA LEWEGO PRIMERA: %s' %(req, key, lprim))
		bp=el17pr.find('RIGHT PRIMER') 
		rightprimlen=bp+25 #indeks długości prawego primera zawsze zaczyna się 25 znaków za pierwszą literą łańcucha znaków 'RIGHT PRIMER'...
		rightprimlen2=rightprimlen+2 #...i kończy dwie pozycje dalej
		rightlen=el17pr[rightprimlen:rightprimlen2] 
		rightprimseq=bp+73 #sekwencja prawego primera zawsze zaczyna się 73 znaki za pierwszą literą łańcucha znaków 'RIGHT PRIMER'
		rightprimseqend=int(rightlen)+rightprimseq #do wartości indeksu pierwszej litery sekwencji primera dodajemy długość primera, żeby uzyskać indeks jego prawej granicy
		rprim=(el17pr[rightprimseq:rightprimseqend]).upper() #wycięcie sekwencji primera z elementu '//pre' strony
		print('GEN %s - EKSON %s -- SEKWENCJA PRAWEGO PRIMERA: %s\n' %(req, key, rprim), '#'*50)
		hg19checkprim(rprim, lprim) #przejście do sprawdzenia obu wyszukanych primerów pod kątem polimorfizmów (funkcja działa tylko jeżeli użytkownik zażądał weryfikacji)

def primer3plussearch():
	'''Funkcja wyszukująca primery w programie Primer 3 Plus. Podstawowe narzędzie używane do tego celu.'''
	driver.get('https://primer3plus.com/cgi-bin/dev/primer3plus.cgi')
	driver.implicitly_wait(2) #daje czas na załadowanie wszystkich elementów na stronie
	elem15=driver.find_element_by_xpath("""//a[@onclick="showTab('tab2','primer3plus_general_primer_picking')"]""") #wybór innej od bieżącej zakładki formularza
	driver2.click(elem15).perform()
	driver2.reset_actions()
	select1=Select(driver.find_element_by_name('PRIMER_MISPRIMING_LIBRARY')) #rozwinięcie listy z kilkoma dostępnymi opcjami
	select1.select_by_visible_text('HUMAN') #wybór opcji primerów dla genomu ludzkiego
	elem16=driver.find_element_by_xpath("""//a[@onclick="showTab('tab1','primer3plus_main_tab')"]""")
	driver2.click(elem16).perform() #powrót do pierwszej widocznej zakładki formularza
	driver2.reset_actions()
	elem17=driver.find_element_by_name('SEQUENCE_TEMPLATE') #wyszukanie okna do wstawienia sekwencji
	elem17.clear()
	elem17.send_keys(prsq) #wprowadzenie sekwencji ze wstawionymi nawiasami klamrowymi
	elem18=driver.find_element_by_name("Pick_Primers")
	driver2.move_to_element(elem18).click().perform()
	driver2.reset_actions()
	driver.implicitly_wait(2) #daje czas na załadowanie wszystkich elementów na stronie
	try:
		assert 'ok 0' not in driver.page_source, '\nNIE ZNALEZIONO PRIMERÓW DO JEDNEGO Z PODANYCH EKSONÓW (EKSON %s)! WPROWADŹ RĘCZNIE SEKWENCJĘ DO PROGRAMU PRIMER 3 PLUS, ŻEBY SPRAWDZIĆ PRZYCZYNY.\n' % key#sprawdzenie, czy program Primer3Plus nie był w stanie zaprojektować primerów
	except AssertionError as aserr:
		print(aserr) #jeżeli nie można było zaprojektować starterów do jednego z fragmentów, program informuje o tym, ale nie przerywa działania i przechodzi do dalszej analizy reszty eksonów
	else: #zachowanie programu jeżeli primery dla danego eksonu zostały znalezione
		elem19=driver.find_element_by_xpath('//input[@id="PRIMER_LEFT_0_SEQUENCE"]')
		lprim=(elem19.get_attribute('defaultValue')).upper() #pobranie sekwencji primera lewego z elementu 19.
		print('','#'*50, '\nGEN %s - EKSON %s -- SEKWENCJA LEWEGO PRIMERA: %s' %(req, keyfull, lprim))
		elem20=driver.find_element_by_xpath('//input[@id="PRIMER_RIGHT_0_SEQUENCE"]')
		rprim=(elem20.get_attribute('defaultValue')).upper() #pobranie sekwencji primera prawego z elementu 20.
		print('GEN %s - EKSON %s -- SEKWENCJA PRAWEGO PRIMERA: %s\n' %(req, keyfull, rprim), '#'*50)
		hg19checkprim(rprim, lprim) #przejście do sprawdzenia obu wyszukanych primerów pod kątem polimorfizmów (funkcja działa tylko jeżeli użytkownik zażądał weryfikacji)

def reverseprimer(primer):
	'''Funkcja przekształcająca primer na jego komplementarną (pasującą sekwencją) formę 5'-3' (jest to oznaczenie kierunku nici DNA). Fragment genu uzyskany w notacji hg19 ze strony UCSC zawiera sekwencję o odwrotnym przebiegu niż jeden z primerów dla danego eksonu. W związku z tym, aby możliwe było prawidłowe wyszukanie położenia tego primera na późniejszych etapach weryfikacji sekwencji, trzeba uzyskać wygląd analogicznego miejsca na drugiej nici DNA.'''
	rev=[]
	for x in primer.upper():
	    if 'A' in x:
	        rev.append('T') #z adeniną (A) w prawidłowym DNA zawsze paruje się tymina (T)
	    elif 'T' in x:
	        rev.append('A')#...i odwrotnie
	    elif 'G' in x:
	        rev.append('C')#z guaniną (G) w prawidłowym DNA zawsze paruje się cytozyna (C)
	    elif 'C' in x:
	        rev.append('G')#... i odwrotnie
	rev=rev[::-1] #oprócz dobrania zasad pasujących na drugiej nici, konieczne jest odwrócenie sekwencji
	rev=''.join(rev)
	return str(rev)

def hg19checkprim(rprim, lprim):
	if verifyflag == 1: #zachowanie programu, gdy użytkownik zażądał weryfikacji sekwencji
		rprim=reverseprimer(rprim) #do wyszukiwania w genomie hg19 uzyskana sekwencja primera musi zostać odwrócona i zamieniona na komplementarne nukleotydy
		seqfastahg19=seqfastahg19orig.upper() #sekwencje primerów wypisane są dużymi literami i tak również powinna wyglądać sekwencja genomu
		seqfastahg19=seqfastahg19.replace('\n','') #pozbywa się znaków nowego wiersza ze źródła strony
		_,seqfastahg19=seqfastahg19.split('REPEATMASKING=NONE') #usuwanie niepotrzebnych fragmentów kodu źródłowego zawierającego sekwencję genu
		seqfastahg19,_=seqfastahg19.split('</PRE>') #usuwanie niepotrzebnych fragmentów kodu źródłowego zawierającego sekwencję genu
		if direction == '-': #przy genie transkrybowanym od prawej do lewej
			lprimhg19en=chend - seqfastahg19.find(lprim) #rzeczywisty początek sekwencji primera lewego na chromosomie wg wersji genomu hg19
			lprimhg19st=lprimhg19en - len(lprim) + 1 #rzeczywisty koniec sekwencji primera lewego na chromosomie wg wersji genomu hg19
			assert seqfastahg19.find(lprim) != -1, '\n\nWYSTĄPIŁ PROBLEM Z WYSZUKANIEM SEKWENCJI PRIMERA DLA EKSONU %s W GENOMIE hg19. NIEMOŻLIWA JEST WERYFIKACJA STARTERÓW POD KĄTEM POLIMORFIZMÓW.\n\nMożliwe, że primer został zaprojektowany poza sekwencją referencyjną genu. W takim przypadku rekomendowane jest ponowne uruchomienie programu i analiza wszystkich eksonów bez włączonej opcji weryfikacji sekwencji, lub nieuwzględnianie %s eksonu w zakresie analizy.' %(keyfull, keyfull)
			rprimhg19en=chend - seqfastahg19.find(rprim) #rzeczywisty początek sekwencji primera prawego na chromosomie wg wersji genomu hg19
			rprimhg19st=rprimhg19en - len(rprim) + 1 #rzeczywisty koniec sekwencji primera lewego na chromosomie wg wersji genomu hg19
		else: #przy genie transkrybowanym od lewej do prawej
			lprimhg19st=seqfastahg19.find(lprim) + chstart #rzeczywisty początek sekwencji primera lewego na chromosomie wg wersji genomu hg19
			lprimhg19en=lprimhg19st + len(lprim) - 1 #rzeczywisty koniec sekwencji primera lewego na chromosomie wg wersji genomu hg19
			assert seqfastahg19.find(lprim) != -1, '\n\nWYSTĄPIŁ PROBLEM Z WYSZUKANIEM SEKWENCJI PRIMERA DLA EKSONU %s W GENOMIE hg19. NIEMOŻLIWA JEST WERYFIKACJA STARTERÓW POD KĄTEM POLIMORFIZMÓW.\n\n\nMożliwe, że primer został zaprojektowany poza sekwencją referencyjną genu. W takim przypadku rekomendowane jest ponowne uruchomienie programu i analiza wszystkich eksonów bez włączonej opcji weryfikacji sekwencji, lub nieuwzględnianie %s eksonu w zakresie analizy.' %(keyfull, keyfull)
			rprimhg19st=seqfastahg19.find(rprim) + chstart #rzeczywisty początek sekwencji primera prawego na chromosomie wg wersji genomu hg19
			rprimhg19en=rprimhg19st + len(rprim) - 1 #rzeczywisty koniec sekwencji primera lewego na chromosomie wg wersji genomu hg19		
		lprim19range=range(lprimhg19st, lprimhg19en+1)
		rprim19range=range(rprimhg19st, rprimhg19en+1)
		for n in lprim19range: #pętla wyszukująca, czy dany nukleotyd primera nie zawiera na swojej pozycji (ustalonej względem genomu hg19) polimorfizmu, który może zaburzyć reakcję sekwencjonowania 
			Lgnomadrecord='<td id="td-pop-acs-EuropeanNon-Finnish'+str(ch)+'-'+str(n) #fragment z informacją o polimorfizmie w populacji europejskiej (bez fińskiej) w danej pozycji genomu
			Lchecksnp=gnomadsrc.find(Lgnomadrecord) #wyszukiwanie fragmentu 'Lgnomadrecord' w źródle strony- jeżeli nie zostanie znaleziony (Lchecksnp == -1) pętla kontynuuje wyszukiwanie kolejnych pozycji
			if Lchecksnp == -1:
				continue
			else: #jeżeli fragment 'Lgnomadrecord' zostanie znaleziony
				Lgnomadrest=gnomadsrc[Lchecksnp:] #odcięcie wszystkich poprzedzających 'Lgnomadrecord' informacji ze źródła strony (przyspiesza dalsze wyszukiwanie)
				Llbrdrfrq=Lgnomadrest.find('>') 
				Lrbrdrfrq=Lgnomadrest.find('</td>')
				Llsnpfreq1=Lgnomadrest[Llbrdrfrq+1:Lrbrdrfrq] #zaraz po symbolu '>' i przed fragmentem '</td>' następuje liczba, mówiąca o ilości przypadków z danym genotypem heterozygotycznym (z polimorfizmem tylko w jednym allelu) w populacji europejskiej (nie fińskiej)
				Lgnomadrest2=Lgnomadrest[Lrbrdrfrq+4:] # odcina poprzednio wyszukany fragment ze źródła strony (+4 dodatkowo wycina ze źródła strony pierwszy fragment '</td>' (kolejny taki fragment jest istotny dla dalszego wyszukiwania))
				Llbrdrfrq2=Lgnomadrest2.find('class="hidden">')
				Lrbrdrfrq2=Lgnomadrest2.find('</td>')
				Llsnpfreq2=Lgnomadrest2[Llbrdrfrq2+15:Lrbrdrfrq2] #15 znaków po fragemncie 'class="hidden">' i przed fragmentem '</td>' następuje liczba, mówiąca o ilości wszystkich osób, na które przypadają homo- i heterozygotyczne polimorfizmy w populacji europejskiej (nie fińskiej)
				Lgnomadrest3=Lgnomadrest2[Lrbrdrfrq2+4:] #odcina poprzednio wyszukany fragment ze źródła strony (+4 dodatkowo wycina ze źródła strony pierwszy fragment '</td>' (kolejny taki fragment jest istotny dla dalszego wyszukiwania))
				Llbrdrfrq3=Lgnomadrest3.find('class="hidden">')
				Lrbrdrfrq3=Lgnomadrest3.find('</td>')
				Llsnpfreq3=Lgnomadrest3[Llbrdrfrq3+15:Lrbrdrfrq3] #15 znaków po fragemncie 'class="hidden">' i przed fragmentem '</td>' następuje liczba, mówiąca o ilości przypadków z danym genotypem homozygotycznym w populacji europejskiej (nie fińskiej)
				homnhet=int(Llsnpfreq1)+int(Llsnpfreq3) #suma wszystkich przypadków z wykrytymi polimorfizmami (homozygot i heterozygot)
				if homnhet != 0: #uniknięcie próby dzielenia przez 0
					if (homnhet)/int(Llsnpfreq2) >= 1/8000: # informacja dla użytkownika pojawia się tylko wtedy, gdy istnieje realna szansa wpływu polimorfizmu na niepowodzenie rekacji sekwencjonowania (przyjęto, że wartością graniczną będzie częstość większa od 1 na 8000 przypadków)
						if direction == '-':
							Lsnpprimindex=lprimhg19en-n #ustala pozycję, odejmując aktualne położenie względem genomu hg19 od pozycji początku primera względem genomu hg19
						else:
							Lsnpprimindex=n-lprimhg19st
						if Lsnpprimindex != (len(lprim)-1): #scenariusz w przypadku gdy polimorfizm nie występuje na ostatnim miejscu sekwencji primera
							if Llsnpfreq3 == '0': #informacja wyświetlana gdy nie wykryto żadnych homozygot
								print('\n'+'-'*30+'\n W sekwencji primera lewego na wskazanej poniżej pozycji:\n\n',lprim[:Lsnpprimindex]+'-->'+lprim[Lsnpprimindex]+'<--'+lprim[Lsnpprimindex+1:]+'\n'+'\nwystępuje zmienność osobnicza w populacji europejskiej (nie wliczając populacji fińskiej) o częstości %s na %s przypadków. Starter zaprojektowany w takim miejscu może spowodować niepowodzenie reakcji sekwencjonowania. Rozważ użycie innego zestawu primerów.\n' % (homnhet, Llsnpfreq2) +'-'*30)
							else: #informacja wyświetlana gdy wykryto genotypy homozygotyczne
								print('\n'+'-'*30+'\n W sekwencji primera lewego na wskazanej poniżej pozycji:\n\n',lprim[:Lsnpprimindex]+'-->'+lprim[Lsnpprimindex]+'<--'+lprim[Lsnpprimindex+1:]+'\n'+'\nwystępuje zmienność osobnicza w populacji europejskiej (nie wliczając populacji fińskiej) o częstości %s na %s przypadków (w tym %s przypadków homozygotycznych). Starter zaprojektowany w takim miejscu może spowodować niepowodzenie reakcji sekwencjonowania. Rozważ użycie innego zestawu primerów.\n' % (homnhet, Llsnpfreq2, Llsnpfreq3) +'-'*30)
						else: #scenariusz w przypadku gdy polimorfizm występuje na ostatnim miejscu sekwencji primera
							if Llsnpfreq3 == '0': #informacja wyświetlana gdy nie wykryto żadnych homozygot
								print('\n'+'-'*30+'\n W sekwencji primera lewego na wskazanej poniżej pozycji:\n\n',lprim[:Lsnpprimindex]+'-->'+lprim[Lsnpprimindex]+'<--'+'\n'+'\nwystępuje zmienność osobnicza w populacji europejskiej (nie wliczając populacji fińskiej) o częstości %s na %s przypadków. Starter zaprojektowany w takim miejscu może spowodować niepowodzenie reakcji sekwencjonowania. Rozważ użycie innego zestawu primerów.\n' % (homnhet, Llsnpfreq2) +'-'*30)
							else: #informacja wyświetlana gdy wykryto genotypy homozygotyczne
								print('\n'+'-'*30+'\n W sekwencji primera lewego na wskazanej poniżej pozycji:\n\n',lprim[:Lsnpprimindex]+'-->'+lprim[Lsnpprimindex]+'<--'+'\n'+'\nwystępuje zmienność osobnicza w populacji europejskiej (nie wliczając populacji fińskiej) o częstości %s na %s przypadków (w tym %s przypadków homozygotycznych). Starter zaprojektowany w takim miejscu może spowodować niepowodzenie reakcji sekwencjonowania. Rozważ użycie innego zestawu primerów.\n' % (homnhet, Llsnpfreq2, Llsnpfreq3) +'-'*30) 
				continue
		rprim=reverseprimer(rprim) #zamienia sekwencję primera prawego na identyczną do uzyskanej z programu Primer 3.0 lub Primer 3 Plus
		for n in rprim19range: #pętla wyszukująca, czy dany nukleotyd primera nie zawiera na swojej pozycji (ustalonej względem genomu hg19) polimorfizmu, który może zaburzyć reakcję sekwencjonowania 
			Rgnomadrecord='<td id="td-pop-acs-EuropeanNon-Finnish'+str(ch)+'-'+str(n) #fragment z informacją o polimorfizmie w populacji europejskiej (bez fińskiej) w danej pozycji genomu
			Rchecksnp=gnomadsrc.find(Rgnomadrecord) #wyszukiwanie fragmentu 'Rgnomadrecord' w źródle strony- jeżeli nie zostanie znakeziony (Rchecksnp == -1) pętla kontynuuje wyszukiwanie kolejnych pozycji
			if Rchecksnp == -1:
				continue
			else: #jeżeli fragment 'Rgnomadrecord' zostanie znaleziony
				Rgnomadrest=gnomadsrc[Rchecksnp:] #odcięcie wszystkich poprzedzających 'Rgnomadrecord' informacji ze źródła strony (przyspiesza dalsze wyszukiwanie)
				Rlbrdrfrq=Rgnomadrest.find('>') 
				Rrbrdrfrq=Rgnomadrest.find('</td>')
				Rlsnpfreq1=Rgnomadrest[Rlbrdrfrq+1:Rrbrdrfrq] #zaraz po symbolu '>' i przed fragmentem '</td>' następuje liczba, mówiąca o ilości przypadków z danym genotypem heterozygotycznym (z polimorfizmem tylko w jednym allelu) w populacji europejskiej (nie fińskiej)
				Rgnomadrest2=Rgnomadrest[Rrbrdrfrq+4:] #odcina poprzednio wyszukany fragment ze źródła strony (+4 dodatkowo wycina ze źródła strony pierwszy fragment '</td>' (kolejny taki fragment jest istotny dla dalszego wyszukiwania))
				Rlbrdrfrq2=Rgnomadrest2.find('class="hidden">')
				Rrbrdrfrq2=Rgnomadrest2.find('</td>')
				Rlsnpfreq2=Rgnomadrest2[Rlbrdrfrq2+15:Rrbrdrfrq2] #15 znaków po fragemncie 'class="hidden">' i przed fragmentem '</td>' następuje liczba, mówiąca o ilości wszystkich osób, na które przypadają homo- i heterozygotyczne polimorfizmy w populacji europejskiej (nie fińskiej)
				Rgnomadrest3=Rgnomadrest2[Rrbrdrfrq2+4:] #odcina poprzednio wyszukany fragment ze źródła strony (+4 dodatkowo wycina ze źródła strony pierwszy fragment '</td>' (kolejny taki fragment jest istotny dla dalszego wyszukiwania))
				Rlbrdrfrq3=Rgnomadrest3.find('class="hidden">')
				Rrbrdrfrq3=Rgnomadrest3.find('</td>')
				Rlsnpfreq3=Rgnomadrest3[Rlbrdrfrq3+15:Rrbrdrfrq3] #15 znaków po fragemncie 'class="hidden">' i przed fragmentem '</td>' następuje liczba, mówiąca o ilości przypadków z danym genotypem homozygotycznym w populacji europejskiej (nie fińskiej)
				homnhet=int(Rlsnpfreq1)+int(Rlsnpfreq3) #suma wszystkich przypadków z wykrytymi polimorfizmami (homozygot i heterozygot)
				if homnhet != 0: #uniknięcie próby dzielenia przez 0
					if (homnhet)/int(Rlsnpfreq2) >= 1/8000: # informacja dla użytkownika pojawia się tylko wtedy, gdy istnieje realna szansa wpływu polimorfizmu na niepowodzenie rekacji sekwencjonowania (przyjęto, że wartością graniczną będzie częstość większa od 1 na 8000 przypadków)
						if direction == '-':
							Rsnpprimindex=((rprimhg19en-n)*(-1))-1 #ustala pozycję mutacji punktowej na komplementarnym do przeszukiwanej nici DNA primerze
						else:
							Rsnpprimindex=((n-rprimhg19st)*(-1))-1
						if Rsnpprimindex != -1: #scenariusz w przypadku gdy polimorfizm nie występuje na ostatnim miejscu sekwencji primera	
							if Rlsnpfreq3 == '0': #informacja wyświetlana gdy nie wykryto żadnych homozygot
								print('\n'+'-'*30+'\n W sekwencji primera prawego na wskazanej poniżej pozycji:\n\n',rprim[:Rsnpprimindex]+'-->'+rprim[Rsnpprimindex]+'<--'+rprim[Rsnpprimindex+1:]+'\n'+'\nwystępuje zmienność osobnicza w populacji europejskiej (nie wliczając populacji fińskiej) o częstości %s na %s przypadków. Starter zaprojektowany w takim miejscu może spowodować niepowodzenie reakcji sekwencjonowania. Rozważ użycie innego zestawu primerów.\n' % (homnhet, Rlsnpfreq2) +'-'*30)
							else: #informacja wyświetlana gdy wykryto genotypy homozygotyczne
								print('\n'+'-'*30+'\n W sekwencji primera prawego na wskazanej poniżej pozycji:\n\n',rprim[:Rsnpprimindex]+'-->'+rprim[Rsnpprimindex]+'<--'+rprim[Rsnpprimindex+1:]+'\n'+'\nwystępuje zmienność osobnicza w populacji europejskiej (nie wliczając populacji fińskiej) o częstości %s na %s przypadków (w tym %s przypadków homozygotycznych). Starter zaprojektowany w takim miejscu może spowodować niepowodzenie reakcji sekwencjonowania. Rozważ użycie innego zestawu primerów.\n' % (homnhet, Rlsnpfreq2, Rlsnpfreq3) +'-'*30)
						else: #scenariusz w przypadku gdy polimorfizm występuje na ostatnim miejscu sekwencji primera
							if Rlsnpfreq3 == '0': #informacja wyświetlana gdy nie wykryto żadnych homozygot
								print('\n'+'-'*30+'\n W sekwencji primera prawego na wskazanej poniżej pozycji:\n\n',rprim[:Rsnpprimindex]+'-->'+rprim[Rsnpprimindex]+'<--'+'\n'+'\nwystępuje zmienność osobnicza w populacji europejskiej (nie wliczając populacji fińskiej) o częstości %s na %s przypadków. Starter zaprojektowany w takim miejscu może spowodować niepowodzenie reakcji sekwencjonowania. Rozważ użycie innego zestawu primerów.\n' % (homnhet, Rlsnpfreq2) +'-'*30)
							else: #informacja wyświetlana gdy wykryto genotypy homozygotyczne
								print('\n'+'-'*30+'\n W sekwencji primera prawego na wskazanej poniżej pozycji:\n\n',rprim[:Rsnpprimindex]+'-->'+rprim[Rsnpprimindex]+'<--'+'\n'+'\nwystępuje zmienność osobnicza w populacji europejskiej (nie wliczając populacji fińskiej) o częstości %s na %s przypadków (w tym %s przypadków homozygotycznych). Starter zaprojektowany w takim miejscu może spowodować niepowodzenie reakcji sekwencjonowania. Rozważ użycie innego zestawu primerów.\n' % (homnhet, Rlsnpfreq2, Rlsnpfreq3) +'-'*30)						
				continue
		print('\nZweryfikowano zmienności w obrębie pary primerów dla eksonu %s.\n' % keyfull)

while True:
	req=input('\nWprowadź nazwę genu dla wyszukania primerów [np. BRCA1 , FTL , ECM1]:\n')
	if not req:
		pass #jeżeli użytkownik nie wprowadził żadnej nazwy, skrypt ponownie wyświetla zapytanie
	else: #gdy użytkownik wpisze nazwę genu
		req=req.upper() #zabezpieczenie w przypadku gdy użytkownik wpisze nazwę małymi literami
		break
seqver=input('\nWprowadź oznaczenie LRG lub NM dla transkryptu tego genu [zgodnie z formatem z przykładów: LRG_292 , LRG_292t1 , NM_007294 , NM_007294t1]:\n')
seqver=seqver.replace(' ','') #usuwa spacje w nazwie transkryptu, co ułatwia późniejsze przetworzenie przez program
seqexo=[] #lista przechowująca numery analizowanych eksonów w postaci liczb całkowitych
allflag=0 #wyłączony znacznik polecenia zaprojektowania primerów do wszystkich sekwencji kodujących
verifyflag=0 #flaga weryfikacji primerów pod kątem polimorfizmów

while True: #zapytanie o weryfikację sekwencji primerów względem bazy danych o mutacjach w DNA
	verif=input('\nCzy program ma weryfikować sekwencje uzyskanych primerów pod kątem polimorfizmów? Wydłuży to czas oczekiwania na wynik. [wpisz T dla TAK lub N dla NIE]:\n')
	if verif == 'T' or verif == 't': #odpowiedź twierdząca
		verifyflag=1 #włączenie znacznika polecenia weryfikacji primerów
		break
	if verif == 'N' or verif == 'n': #odpowiedź przecząca
		verifyflag=0 #wyłączenie znacznika polecenia weryfikacji primerów
		break
	else:
		pass #pętla ponowie wyświetla zapytanie jeżeli użytkownik nie wprowadził odpowiedniego symbolu

while True:
	if len(seqexo) == 0: #zachowanie pętli przy pierwszym wprowadzanym eksonie
		seqex=input('\nPodaj pierwszy numer eksonu dla zaprojektowania primerów [lub wprowadź A , żeby wybrać wszystkie sekwencje kodujące]:\n')
		if seqex == 'A' or seqex == 'a': #wprowadzenie znaku 'x' powoduje wyjście z pętli i rozpoczyna tworzenie primerów
			allflag=1 #włączenie znacznika polecenia zaprojektowania primerów do wszystkich sekwencji kodujących i rozpoczęcie tworzenia primerów
			break
		else:
			seqexo.append(int(seqex))
	else: #zachowanie pętli przy każdym kolejnym wprowadzanym eksonie
		seqex=input('\nPodaj kolejny numer eksonu dla zaprojektowania primerów [lub wprowadź X , żeby rozpocząć]:\n')	
		if seqex == 'X' or seqex == 'x': #wprowadzenie znaku 'x' powoduje wyjście z pętli i rozpoczyna tworzenie primerów
			break
		else:
			seqexo.append(int(seqex)) #modyfikuje w miejscu listę z numerami eksonów do analizy, dodając te interesujące użytkownika (wprowadzenie numeru eksonu, którego dany gen nie posiada, nie powoduje żadnej akcji związanej z jego wyszukiwaniem na późniejszych etapach, z uwagi na porównywanie liczby otrzymanych z serwisu UCSC rekordów i ich automatyczną numerację)


driver = webdriver.Chrome() #sterownik do danej wersji przeglądarki (Google Chrome)
driver2=ActionChains(driver) #utworzenie instancji ActionChains (umożliwia wykonywanie dodatkowych łańcuchów czynności przy przechodzeniu stron internetowych)

if 'LRG' in seqver: #jeżeli użytkownik w zamiast nazwy NM_ transkryptu użył nomenklatury LRG_
	seqvert=seqver.find('t') #sprawdzenie występowania oznaczenia konkretnego wariantu splicingowego w nazwie transkryptu i odcięcie go od niej
	if seqvert == -1: #jeżeli nie odnaleziono oznaczenia wariantu splicingowego
		seqvershort2=seqver
	else: #jeżeli odnaleziono oznaczenie wariantu splicingowego, program rozdziela jego numer i resztę nazwy (funkcja potrzebna do późniejszych interakcji i wyszukiwań)
		seqvershort2=seqver[:seqvert]
		seqverappend=seqver[seqvert:]
	driver.get('https://www.lrg-sequence.org/') #strona zawierająca bazę danych sekwencji LRG
	elemlrg = driver.find_element_by_id("search_id") #znalezienie okna wyszukiwania
	elemlrg.clear()
	elemlrg.send_keys(seqvershort2) #wprowadzenie nazwy genu
	elemlrg.send_keys(Keys.RETURN)
	driver.implicitly_wait(2) #czas na załadowanie wszystkich elementów na stronie
	elemlrg2=driver.find_element_by_partial_link_text(seqvershort2) #odnalezienie linku z interesującym nas transkryptem 
	driver2.click(elemlrg2).perform() #kliknięcie linku z transkryptem powoduje otwarcie nowego okna
	driver2.reset_actions()
	handles = list(driver.window_handles) #lista nazw wszystkich okien przeglądarki obecnie otwartych (2 okna)
	driver.switch_to_window(handles[0]) #przełączenie i zamknięcie starej karty
	driver.close()
	driver.switch_to_window(handles[1])	#przełączenie sterownika na nowootwarte okno
	lrgpagesrc=driver.page_source #pobranie źródła strony do analizy
	Lnmbrdr=lrgpagesrc.find("'NM_") #pobranie nazwy NM transkryptu ze źródła strony
	nmfromlrg=lrgpagesrc[Lnmbrdr+1:] #przeszukiwanie reszty strony po fragmencie "'NM_" by odnaleźć kolejny apostrof, oznaczający koniec numeru transkryptu
	Rnmbrdr=nmfromlrg.find("'")
	nmfromlrg=lrgpagesrc[Lnmbrdr+1:Lnmbrdr+Rnmbrdr+1] #pobranie nazwy transkryptu
	seqver=nmfromlrg+seqverappend #przypisanie go do zmiennej 'seqver' zamiast wprowadzonej pierwotnie nazwy LRG

#wyszukiwanie pełnej sekwencji w wersji genomu hg19
if verifyflag == 1: #wykonywanie tylko jeżeli użytkownik zażądał weryfikacji sekwencji primerów
	print('\n'+'-'*30+'\nTrwa wyszukiwanie sekwencji genu dla wersji hg19...')
	driver.get("https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&lastVirtModeType=default&lastVirtModeExtraState=&virtModeType=default&virtMode=0&nonVirtPosition=&position=chr21%3A33031597-33041570&hgsid=689173155_Hg58krwf2UsMmqb0tKxdNY5aXCVr") #strona główna UCSC genomu hg19
	elemx = driver.find_element_by_name("hgt.positionInput") #znalezienie okna wyszukiwania
	elemx.clear()
	elemx.send_keys(req) #wprowadzenie nazwy genu
	elemx.send_keys(Keys.RETURN)
	if 't' in seqver: #sprawdzenie występowania oznaczenia konkretnego wariantu splicingowego w nazwie NM transkryptu i odcięcie go od nazwy
		seqvert=seqver.find('t')
		seqvershort1=seqver[:seqvert]
	else:
		seqvershort1=seqver
	assert "Sorry, couldn't locate" not in driver.page_source, '\n\n\nGEN O NAZWIE PODANEJ PRZEZ UŻYTKOWNIKA NIE ISTNIEJE' #upewnienie się, że nazwa genu wpisana przez użytkownika jest poprawna
	assert seqvershort1 in driver.page_source, '\n\n\nNIE ZNALEZIONO PODANEGO OZNACZENIA TRANSKRYPTU W BAZIE DANYCH.\n\nSPRAWDŹ, CZY NAZWA TRANSKRYPTU NIE ZAWIERA BŁĘDÓW, LUB CZY FAKTYCZNIE DOTYCZY WYBRANEGO GENU.'
	elem2x=driver.find_element_by_partial_link_text(seqvershort1) #odnalezienie linku z interesującym nas transkryptem (RefSeq)
	driver2.click(elem2x).perform() #kliknięcie linku z transkryptem
	driver2.reset_actions()
	elem3x=driver.find_element_by_name("hgt.positionInput") #znalezienie okna wyszukiwania
	y=120 #wartość przesunięcia kursora ku dołowi względem okna wyszukiwania
	driver2.move_to_element_with_offset(elem3x, -200, y).click().perform() #przesunięcie kursora względem okna wyszukiwania na pozycję w oknie GENCODE 24
	driver2.reset_actions()
	if '.' in seqver: #pętla sprawdzająca występowanie liczb po kropce w wersji NM transkryptu i odcinająca je od nazwy
		seqverdot=seqver.find('.')
		seqvershort=seqver[:seqverdot] #nazwa transkryptu bez elementów po kropce
	elif 't' in seqver: #sprawdzenie występowania oznaczenia konkretnego wariantu splicingowego w nazwie NM transkryptu i odcięcie go od nazwy
		seqvert=seqver.find('t')
		seqvershort=seqver[:seqvert]
	else:
		seqvershort=seqver
	while True: #sprawdza, czy wybrana została przez kursor odpowiednia wersja transkryptu
		if 't' in seqver: #jeżeli użytkownik w nazwie sprecyzował, o który wariant splicingowy chodzi
			vari='transcript variant %s' % seqver[seqvert+1:] #nazwa wariantu, jaka musi pojawić się w źródle strony po kliknięciu w odpowiedni link
			if 'UCSC Genome Browser' in driver.page_source: #upewnia się, że po kliknięciu fragmentu okna bez linku do następnej strony nie zostanie wykonane przejście wstecz w historii przeglądarki
				y+=2
				elemLOOP=driver.find_element_by_name("hgt.positionInput")
				driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
				driver2.reset_actions()
				continue
			elif seqvershort not in driver.page_source: #jeżeli pomimo otwarcia linku nie została kliknięta odpowiednia wersja transkryptu
				driver.back() #powrót do poprzedniego okna
				y+=5 
				elemLOOP=driver.find_element_by_name("hgt.positionInput")
				driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
				driver2.reset_actions()
				continue
			else:
				if vari not in driver.page_source: #jeżeli mimo klinięcia odpowiedniej wersji transkryptu w źródle strony nie ma wzmianki o nazwie wariantu splicingowego
					driver.back() #powrót do poprzedniego okna
					y+=5 
					elemLOOP=driver.find_element_by_name("hgt.positionInput")
					driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
					driver2.reset_actions()
					continue
				else:
					#wyszukiwanie w źródle strony informacji, czy nić transkrybowana jest od lewej do prawej, czy na odwrót
					hg19stranddirection=driver.page_source.find('Strand:</b> ')
					direction=driver.page_source[hg19stranddirection+12] #po 12 znakach od pierwszej litery fragmentu 'Strand:</b> ' w źródle strony następuje symbol (+), oznaczający transkrypcję od lewej do prawej, lub (-), oznaczający transkrypcję od prawej do lewej	
					break #jeżeli kliknięto w odpowiednią wersję transkryptu program wychodzi z pętli
		else: #jeżeli użytkownik nie sprecyzował konkretnej nazwy wariantu splicingowego
			if 'UCSC Genome Browser' in driver.page_source: #upewnia się, że po kliknięciu fragmentu okna bez linku do następnej strony nie zostanie wykonane przejście wstecz w historii
				y+=2
				elemLOOP=driver.find_element_by_name("hgt.positionInput")
				driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
				driver2.reset_actions()
				continue
			elif seqvershort not in driver.page_source: #jeżeli pomimo otwarcia linku nie została kliknięta odpowiednia wersja transkryptu
				driver.back() #powrót do poprzedniego okna
				y+=5
				elemLOOP=driver.find_element_by_name("hgt.positionInput")
				driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
				driver2.reset_actions()
				continue
			else: #po kliknięciu w odpowiedni link
				#wyszukiwanie w źródle strony informacji, czy nić transkrybowana jest od lewej do prawej, czy na odwrót
				hg19stranddirection=driver.page_source.find('Strand:</b> ')
				direction=driver.page_source[hg19stranddirection+12] #po 12 znakach od pierwszej litery fragmentu 'Strand:</b> ' w źródle strony następuje symbol (+), oznaczający transkrypcję od lewej do prawej, lub (-), oznaczający transkrypcję od prawej do lewej	
				break #jeżeli kliknięto w odpowiednią wersję transkryptu program wychodzi z pętli

	elem4x=driver.find_element_by_partial_link_text('Genomic Sequence') #przejście do formularza dotyczącego parametrów konkretnej sekwencji
	driver2.click(elem4x).perform()
	driver2.reset_actions()
	
	#poniżej uzupełnienie formularza dla sekwencji w formacie FASTA (służy wyłącznie do uzyskania liczby eksonów (hg19exoncntctrl) danego genu w notacji hg19 w celu późniejszego skontrolowania zgodności z liczbą eksonów w hg38)
	elem5c=driver.find_element_by_xpath("//input[@name='hgSeq.promoter'][@type='CHECKBOX']")
	if elem5c.get_property('checked'):
		driver2.click(elem5c) #jeżeli pole 'upstream by ... bases' (analiza sekwencji DNA w rejonie powyżej badanego genu) jest zaznaczone to odznacza je
	elem6c=driver.find_element_by_xpath("//input[@name='hgSeq.downstream'][@type='CHECKBOX']")
	if elem6c.get_property('checked'):
		driver2.click(elem6c) #jeżeli pole 'downstream by ... bases' (analiza sekwencji DNA w rejonie poniżej badanego genu) jest zaznaczone to odznacza je
	elem7c=driver.find_element_by_xpath("//input[@name='hgSeq.cdsExon'][@type='CHECKBOX']")
	if not elem7c.get_property('checked'):
		driver2.click(elem7c) #zaznacza wyszukiwanie CDS (fragmentów kodujących) danego genu
	elem7nc=driver.find_element_by_xpath("//input[@name='hgSeq.utrExon5'][@type='CHECKBOX']")
	if not elem7nc.get_property('checked'):
		driver2.click(elem7nc) #dodaje wyszukiwanie również niekodujących eksonów na POCZĄTKU badanej sekwencji (koniec 5')- nie będą one analzowane, ale wyjście to służy późniejszej zgodności numeracji eksonów ze stanem rzeczywistym
	elem8c=driver.find_element_by_xpath("//input[@name='hgSeq.utrExon3'][@type='CHECKBOX']")
	if elem8c.get_property('checked'):
		driver2.click(elem8c) #odznacza pozostałe pola formularza (zawierają fragmenty niekodujące genu)
	elem9c=driver.find_element_by_xpath("//input[@name='hgSeq.intron'][@type='CHECKBOX']")
	if elem9c.get_property('checked'):
		driver2.click(elem9c) #odznacza pozostałe pola formularza (zawierają fragmenty niekodujące genu)
	elem10c=driver.find_element_by_xpath("//input[@name='hgSeq.granularity'][@type='radio'][@value='feature']")
	driver2.click(elem10c) #one FASTA record per region (na każdy ekson jest przewidziany dokładnie jeden rekord FASTA)
	driver2.perform()
	driver2.reset_actions()
	elem11c=driver.find_element_by_name("hgSeq.padding5")
	elem11c.clear()
	elem11c.send_keys('150') #wprowadzenie długości sekwencji flankujących CDS (koniec 5')
	elem12c=driver.find_element_by_name("hgSeq.padding3")
	elem12c.clear()
	elem12c.send_keys('150') #wprowadzenie długości sekwencji flankujących CDS (koniec 3')
	elem13c=driver.find_element_by_xpath("//input[@name='hgSeq.casing'][@type='radio'][@value='cds']")
	driver2.click(elem13c).perform() #CDS in upper case, UTR in lower case (wyróżnia dużą czcionką nukleotydy kodujące białka- głównie one są istotne z punku widzenia klinicznego)
	driver2.reset_actions()
	elem14c=driver.find_element_by_name("submit")
	driver2.click(elem14c).perform()
	driver2.reset_actions()
	seqfastac=driver.page_source #Przechowanie kodu źródłowego strony
	seqfastac=seqfastac.replace('\n','') #pozbywa się znaków nowego wiersza ze źródła strony
	seqfastac=seqfastac.split('repeatMasking=none') #dzieli poszczególne rekordy FASTA
	resexonc=[] #tymczasowo zbiera niesformatowane eksony z plików FASTA w jedną listę
	for exon in seqfastac: 
		hgc=exon.find('&gt;hg38')
		if '</pre>' in exon: #postępowanie z pierwszym wycinanym rekordem
			pre=exon.find('</pre>')
			exon=exon[:pre]
			resexonc.append(exon)
		elif '<html' in exon: #odrzuca pierwszy fragment, niezawierający danych o sekwencji
			pass	
		else: #postępowanie z każdym kolejnym wycinanym rekordem
			exon=exon[:hgc]
			resexonc.append(exon)
	hg19exoncntctrl=len(resexonc) #kontrola liczby eksonów w notacji hg19 analizowanego genu
	driver.back() #powrót do poprzedniego formularza

	#poniżej uzupełnienie formularza dla sekwencji w formacie FASTA dla uzyskania całości niepodzielonej sekwencji genu w notacji hg19 (posłuży później do wyszukania dokładnej pozycji zaprojektowanego primera w genomie)- jest to wersja wymagana przez bazę danych weryfikującą zmienności populacyjne sekwencji
	elem5x=driver.find_element_by_xpath("//input[@name='hgSeq.promoter'][@type='CHECKBOX']")
	if not elem5x.get_property('checked'): 
		driver2.click(elem5x) #jeżeli pole 'upstream by ... bases' (analiza sekwencji DNA w rejonie powyżej badanego genu) jest odznaczone to zaznacza je
	elem6x=driver.find_element_by_xpath("//input[@name='hgSeq.downstream'][@type='CHECKBOX']")
	if not elem6x.get_property('checked'):
		driver2.click(elem6x) #jeżeli pole 'downstream by ... bases' (analiza sekwencji DNA w rejonie poniżej badanego genu) jest odznaczone to zaznacza je
	elem7x=driver.find_element_by_xpath("//input[@name='hgSeq.cdsExon'][@type='CHECKBOX']")
	if not elem7x.get_property('checked'):
		driver2.click(elem7x) #zaznacza wyszukiwanie CDS (fragmentów kodujących) danego genu
	elem7xn=driver.find_element_by_xpath("//input[@name='hgSeq.utrExon5'][@type='CHECKBOX']")
	if not elem7xn.get_property('checked'):
		driver2.click(elem7xn) #dodaje wyszukiwanie również niekodujących eksonów na początku badanej sekwencji (koniec 5')
	elem8x=driver.find_element_by_xpath("//input[@name='hgSeq.utrExon3'][@type='CHECKBOX']")
	if not elem8x.get_property('checked'):
		driver2.click(elem8x) #dodaje wyszukiwanie również niekodujących eksonów na końcu sekwencji (koniec 3')
	elem9x=driver.find_element_by_xpath("//input[@name='hgSeq.intron'][@type='CHECKBOX']")
	if not elem9x.get_property('checked'):
		driver2.click(elem9x) #zaznacza wyszukiwanie również fragmentów niekodujących genu (interesuje nas pełna sekwencja)
	elem10x=driver.find_element_by_xpath("//input[@name='hgSeq.granularity'][@type='radio'][@value='gene']")
	driver2.click(elem10x) #one FASTA record per gene (jeden gen utworzy jeden rekord FASTA- ułatwi to ustalenie jego początku w genomie ludzkim i porównanie z położeniem zaprojektowanych primerów)
	driver2.perform()
	driver2.reset_actions()
	elem13x=driver.find_element_by_xpath("//input[@name='hgSeq.casing'][@type='radio'][@value='upper']")
	driver2.click(elem13x).perform() #all in upper case (wszystkie nukleotydy będą wypisane dużymi literami, podobnie jak sekwencje później projektowanych primerów do wyszukania w genie)
	driver2.reset_actions()
	elem14x=driver.find_element_by_name("submit")
	driver2.move_to_element(elem14x).click().perform()
	driver2.reset_actions()
	#zakończenie uzupełniania formularza FASTA
	seqfastahg19orig=driver.page_source #Przechowanie kodu źródłowego strony wg genomu hg19
	#rozpoczęcie przetwarzania koordynatów chromosomowych
	cx=seqfastahg19orig.find('chr') #odnajduje początek lokalizacji chromosomowej
	cy=cx+30 #sekwencja do około 30 symboli dalej na pewno zawiera w swoim przedziale początek genu na chromosomie
	chrfasta19=seqfastahg19orig[cx+3:cy] #wyodrębnia niemal całość koordynatu chromosomowego		
	ch,pos=chrfasta19.split(':') #dzieli koordynat na lewą część, zawierającą numer chromosomu i prawą, zawierającą zakres pozycji sekwencji
	chstart, chend=pos.split('-') #dzieli zakres pozycji na początek i koniec
	chend,_=chend.split(' ') #dodatkowa obróbka fragmentu (do uzyskania samych cyfr)
	chstart=int(chstart) #tworzy liczbę całkowitą z początku lokalizacji sekwencji na chromosomie
	chend=int(chend) #tworzy liczbę całkowitą z końca lokalizacji sekwencji na chromosomie
	#zakończenie przetwarzania koordynatów chromosomowych po uzyskaniu numeru 'ch'- chromosomu, na którym znajduje się sekwencja i 'chstart'- miejsca startu sekwencji na chromosomie wg wersji genomu hg19
	print('Zakończono wyszukiwanie.\n'+'-'*30+'\n')
	#zakończenie interakcji z genomem hg19

#rozpoczęcie wyszukiwania tego samego genu w genomie hg38 (wg przyjętej praktyki laboratoryjnej jest to wersja, względem której należy projektować primery)
print('\n'+'-'*30+'\nTrwa wyszukiwanie sekwencji genu dla wersji hg38...')
driver.get("https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&lastVirtModeType=default&lastVirtModeExtraState=&virtModeType=default&virtMode=0&nonVirtPosition=&position=chr1%3A11102837-11267747&hgsid=688037579_UL2armYMyv76nwrnQ4QBd0KOLbMi") #strona główna UCSC genomu hg38
elem = driver.find_element_by_name("hgt.positionInput") #znalezienie okna wyszukiwania
elem.clear()
elem.send_keys(req) #wprowadzenie nazwy genu
elem.send_keys(Keys.RETURN)
if 't' in seqver: #sprawdzenie występowania oznaczenia konkretnego wariantu splicingowego w nazwie NM transkryptu i odcięcie go od nazwy
	seqvert=seqver.find('t')
	seqvershort1=seqver[:seqvert]
else:
	seqvershort1=seqver
assert "Sorry, couldn't locate" not in driver.page_source, '\n\n\nGEN O NAZWIE PODANEJ PRZEZ UŻYTKOWNIKA NIE ISTNIEJE' #upewnienie się, że nazwa genu wpisana przez użytkownika jest poprawna
assert seqvershort1 in driver.page_source, '\n\n\nNIE ZNALEZIONO PODANEGO OZNACZENIA TRANSKRYPTU W BAZIE DANYCH.\n\nSPRAWDŹ, CZY NAZWA TRANSKRYPTU NIE ZAWIERA BŁĘDÓW, LUB CZY FAKTYCZNIE DOTYCZY WYBRANEGO GENU.'
elem2=driver.find_element_by_partial_link_text(seqvershort1) #odnalezienie linku z interesującym nas transkryptem (RefSeq)
driver2.click(elem2).perform() #kliknięcie linku z transkryptem
driver2.reset_actions()
elem3=driver.find_element_by_name("hgt.positionInput") #znalezienie okna wyszukiwania
y=120 #wartość przesunięcia kursora ku dołowi względem okna wyszukiwania
driver2.move_to_element_with_offset(elem3, -200, y).context_click().perform() #przesunięcie kursora względem okna wyszukiwania na pozycję w oknie GENCODE 24
driver2.reset_actions()

if '.' in seqver: #pętla sprawdzająca występowanie liczb po kropce w wersji NM transkryptu i odcinająca je od nazwy
	seqverdot=seqver.find('.')
	seqvershort=seqver[:seqverdot] #nazwa transkryptu bez elementów po kropce
elif 't' in seqver: #sprawdzenie występowania oznaczenia konkretnego wariantu splicingowego w nazwie NM transkryptu i odcięcie go od nazwy
	seqvert=seqver.find('t')
	seqvershort=seqver[:seqvert]
else:
	seqvershort=seqver

while True: #sprawdza, czy wybrana została przez kursor odpowiednia wersja transkryptu
	if 't' in seqver: #jeżeli użytkownik w nazwie sprecyzował, o który wariant splicingowy chodzi
		vari='transcript variant %s' % seqver[seqvert+1:] #nazwa wariantu, jaka musi pojawić się w źródle strony po kliknięciu w odpowiedni link
		if 'UCSC Genome Browser' in driver.page_source: #upewnia się, że po kliknięciu fragmentu okna bez linku do następnej strony nie zostanie wykonane przejście wstecz w historii
			y+=2
			elemLOOP=driver.find_element_by_name("hgt.positionInput")
			driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
			driver2.reset_actions()
			continue
		elif seqvershort not in driver.page_source: #jeżeli pomimo otwarcia linku nie została kliknięta odpowiednia wersja transkryptu
			driver.back() #powrót do poprzedniego okna
			y+=6
			elemLOOP=driver.find_element_by_name("hgt.positionInput")
			driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
			driver2.reset_actions()
			continue
		else:
			if vari not in driver.page_source: #jeżeli mimo klinięcia odpowiedniej wersji transkryptu w źródle strony nie ma wzmianki o nazwie wariantu splicingowego
				driver.back() #powrót do poprzedniego okna
				y+=6
				elemLOOP=driver.find_element_by_name("hgt.positionInput")
				driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
				driver2.reset_actions()
				continue
			else:
				break #jeżeli kliknięto w odpowiednią wersję transkryptu program wychodzi z pętli
	else:
		if 'UCSC Genome Browser' in driver.page_source: #upewnia się, że po kliknięciu fragmentu okna bez linku do następnej strony nie zostanie wykonane przejście wstecz w historii
			y+=2
			elemLOOP=driver.find_element_by_name("hgt.positionInput")
			driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
			driver2.reset_actions()
			continue
		elif seqvershort not in driver.page_source: #jeżeli pomimo otwarcia linku nie została kliknięta odpowiednia wersja transkryptu
			driver.back() #powrót do poprzedniego okna
			y+=6 
			elemLOOP=driver.find_element_by_name("hgt.positionInput")
			driver2.move_to_element_with_offset(elemLOOP, -200,y).click().perform() #przesunięcie kursora w dół o dodatkową wartość ... i ponowna próba znalezienia transkryptu
			driver2.reset_actions()
			continue
		else:
			break #jeżeli kliknięto w odpowiednią wersję transkryptu program wychodzi z pętli

enstlook=driver.page_source #wyszukanie w źródle strony wersji numeru ENST genu, który potem przyda nam się do weryfikacji w bazie danych
checkenst=0 #flaga informująca, czy na późniejszych etapach trzeba będzie z użyciem narzędzia Biomart przekonwertować nazwę NM_ transkrytpu na ENST
if 'ENST' in enstlook: #jeżeli nazwa jest dostępna w źródle strony UCSC
	enst=enstlook.find('ENST')
	enst=enstlook[enst:enst+40] #40 znaków na pewno zawiera w sobie numer ENST
	enst, _=enst.split('.') #pozbycie się zawartości po kropce, by otrzymać format niezbędny dla wyszukiwania w weryfikacyjnej bazie danych GNOMAD
else:
	checkenst=1 #informacja o tym, że na późniejszych etapach trzeba będzie z użyciem narzędzia Biomart przekonwertować nazwę NM_ transkrytpu na ENST

elem4=driver.find_element_by_partial_link_text('Genomic Sequence')
driver2.click(elem4).perform()
driver2.reset_actions()

#poniżej uzupełnienie formularza dla sekwencji w formacie FASTA dla wersji genomu hg38
elem5=driver.find_element_by_xpath("//input[@name='hgSeq.promoter'][@type='CHECKBOX']")
if elem5.get_property('checked'):
	driver2.click(elem5) #jeżeli pole 'upstream by ... bases' (analiza sekwencji DNA w rejonie powyżej badanego genu) jest zaznaczone to odznacza je
elem6=driver.find_element_by_xpath("//input[@name='hgSeq.downstream'][@type='CHECKBOX']")
if elem6.get_property('checked'):
	driver2.click(elem6) #jeżeli pole 'downstream by ... bases' (analiza sekwencji DNA w rejonie poniżej badanego genu) jest zaznaczone to odznacza je
elem7=driver.find_element_by_xpath("//input[@name='hgSeq.cdsExon'][@type='CHECKBOX']")
if not elem7.get_property('checked'):
	driver2.click(elem7) #zaznacza wyszukiwanie CDS (fragmentów kodujących) danego genu
elem7n=driver.find_element_by_xpath("//input[@name='hgSeq.utrExon5'][@type='CHECKBOX']")
if not elem7n.get_property('checked'):
	driver2.click(elem7n) #dodaje wyszukiwanie również niekodujących eksonów na POCZĄTKU badanej sekwencji (koniec 5')- nie będą one analzowane, ale wyjście to służy późniejszej zgodności numeracji eksonów ze stanem rzeczywistym
elem8=driver.find_element_by_xpath("//input[@name='hgSeq.utrExon3'][@type='CHECKBOX']")
if elem8.get_property('checked'):
	driver2.click(elem8) #odznacza pozostałe pola formularza (zawierają fragmenty niekodujące genu)
elem9=driver.find_element_by_xpath("//input[@name='hgSeq.intron'][@type='CHECKBOX']")
if elem9.get_property('checked'):
	driver2.click(elem9) #odznacza pozostałe pola formularza (zawierają fragmenty niekodujące genu)
elem10=driver.find_element_by_xpath("//input[@name='hgSeq.granularity'][@type='radio'][@value='feature']")
driver2.click(elem10) #one FASTA record per region (na każdy ekson jest przewidziany dokładnie jeden rekord FASTA)
driver2.perform()
driver2.reset_actions()
elem11=driver.find_element_by_name("hgSeq.padding5")
elem11.clear()
elem11.send_keys('150') #wprowadzenie długości sekwencji flankujących CDS (koniec 5')- wartość 150 nukleotydów z lewej i tyle samo z prawej strony sekwencji dodana do fragmentu kodującego o długości maksymalnie 200 par zasad daje łącznie maksymalnie 500-znakowe rekordy (wg przyjętej praktyki laboratoryjnej jest to maksymalna długość, dla jakiej sekwencjonowanie przebiega prawidłowo)
elem12=driver.find_element_by_name("hgSeq.padding3")
elem12.clear()
elem12.send_keys('150') #wprowadzenie długości sekwencji flankujących CDS (koniec 3')- wartość 150 nukleotydów z lewej i tyle samo z prawej strony sekwencji dodana do fragmentu kodującego o długości maksymalnie 200 par zasad daje łącznie maksymalnie 500-znakowe rekordy (wg przyjętej praktyki laboratoryjnej jest to maksymalna długość, dla jakiej sekwencjonowanie przebiega prawidłowo)
elem13=driver.find_element_by_xpath("//input[@name='hgSeq.casing'][@type='radio'][@value='cds']")
driver2.click(elem13).perform() #CDS in upper case, UTR in lower case (wyróżnia dużą czcionką nukleotydy kodujące białka- głównie one są istotne z punku widzenia klinicznego)
driver2.reset_actions()

elem14=driver.find_element_by_name("submit")
driver2.click(elem14).perform()
driver2.reset_actions()
#zakończenie uzupełniania formularza FASTA
seqfasta=driver.page_source #Przechowanie kodu źródłowego strony
print('Zakończono wyszukiwanie.\n'+'-'*30+'\n')

#gdy program nie uzyska informacji o tym, jaki numer ENST ma szukana sekwencja (flaga checkenst == 1), uruchamia narzędzie BioMart do konwersji oznaczenia NM_ na ENST (nazwa ENST jest opcją wymaganą do precyzyjnego określenia genu w weryfikacyjnej bazie danych GNOMAD)
if checkenst == 1:
	driver.get('http://www.ensembl.org/biomart/martview/961a6742438e10721fb8d1d353c2882f')
	select2=Select(driver.find_element_by_name('databasemenu'))
	select2.select_by_visible_text('Ensembl Genes 94') #wybór najnowszej wersji bazy danych
	select3=Select(driver.find_element_by_name('datasetmenu_3'))
	select3.select_by_visible_text('Human genes (GRCh38.p12)') #wybór genów ludzkich
	driver.implicitly_wait(3) #czas na załadowanie elementów na stronie
	elemenst1=driver.find_element_by_class_name('mart_summarypanel_AttFiltHeader') #otwarcie okna filtrów wprowadzanego wejścia
	driver2.click(elemenst1).perform()
	driver2.reset_actions()
	elemenst2=driver.find_element_by_xpath("""//span[@onclick="visibility('hsapiens_gene_ensembl__filtergroup.gene','show');"]""") #wybór opcji GENE
	driver2.click(elemenst2).perform()
	driver2.reset_actions()
	elemenst3=driver.find_element_by_name('hsapiens_gene_ensembl__filtercollection.id_list_limit_xrefs') #wybór opcji 'Input external references ID list [Max 500 advised]'- umożliwienie wprowadzenia nazwy transkryptu zgodnej z podanym symbolem
	driver2.click(elemenst3).perform()
	driver2.reset_actions()
	select4=Select(driver.find_element_by_name('hsapiens_gene_ensembl__filter.id_list_limit_xrefs_filters')) 
	select4.select_by_visible_text('RefSeq mRNA ID(s) [e.g. NM_000014]') #wybór opcji 'RefSeq mRNA ID'- jest to nazwa NM_ transkryptu, uzyskiwana na początku działania programu
	elemenst5=driver.find_element_by_name('hsapiens_gene_ensembl__filter.id_list_limit_xrefs_filters__text') #wyszukanie okna wprowadzania nazwy transkryptu
	elemenst5.clear()
	elemenst5.send_keys(seqvershort) #przesłanie nazwy NM_ transkryptu
	elemenst6=driver.find_element_by_class_name('mart_btn_results')
	driver2.click(elemenst6).perform() #klinięcie zakładki z rezultatami
	driver2.reset_actions() 
	elemenst7=driver.find_elements_by_class_name('mart_td')
	for elem in elemenst7:
		probenst=elem.get_property('outerText') #pobranie atrybutu elementu zawierającego nazwę ENST sekwencji
		if 'ENST' in probenst: #...jeżeli takowa występuje
			enst=probenst


#przetwarzanie rekordów FASTA- początkowo zawierają sekwencje poszczególnych eksonów i dodatkowe, niepotrzebne oznaczenia
seqfasta=seqfasta.replace('\n','') #pozbywa się znaków nowego wiersza ze źródła strony
seqfasta=seqfasta.split('repeatMasking=none') #dzieli poszczególne rekordy FASTA
resexon=[] #tymczasowo zbiera niesformatowane eksony z plików FASTA w jedną listę
for exon in seqfasta: 
	hg=exon.find('&gt;hg38')
	if '</pre>' in exon: #postępowanie z pierwszym wycinanym rekordem
		pre=exon.find('</pre>')
		exon=exon[:pre]
		resexon.append(exon)
	elif '<html' in exon: #odrzuca pierwszy fragment, niezawierający danych o sekwencji
		pass	
	else: #postępowanie z każdym kolejnym wycinanym rekordem
		exon=exon[:hg]
		resexon.append(exon)
hg38exoncntctrl=len(resexon) #kontrola liczby eksonów w notacji hg38 analizowanego genu

if verifyflag == 1: #sprawdzenie zgodności liczby eksonów poszczególnych transkryptów w przypadku, gdy użytkownik zażądał weryfikacji sekwencji
	assert hg19exoncntctrl == hg38exoncntctrl, '\n\n\nWykryto niezgodność wersji transkryptów hg19 i hg38 badanego genu. Nie jest możliwa prawidłowa kontrola polimorfizmów. Zalecane jest ponowne uruchomienie programu bez włączonej opcji weryfikacji sekwencji.'
#zakończenie przetwarzania rekordów FASTA

rawexon={i+1:x for (i,x) in enumerate(resexon)} #przypisanie 'czystych' sekwencji poszczególnych eksonów do słownika, wraz z odpowiadającymi im numerami


'''Poniżej rozpoczęcie pętli analizującej łańcuchy i wstawiającej miejsca dla projektowania starterów w programie Primer 3.0/ Primer 3 Plus.Zasadą jest analiza maksymalnie 200-nukleotydowych części i ich 150-nukleotydowych marginesów 
(z doświadczeń wynika, że maksymalnie około 500pz można na raz bezbłędnie sekwencjonować)). Żeby wskazać programowi projektującemu startery dla jakiej części łańcucha powinien ich szukać, należy wstawić nawiasy 
klamrowe [] pomiędzy interesującą nas sekwencję. W założeniu interesuje nas cała sekwencja kodująca i po 30 nukletydów po każdej z jej stron. Doświadczenia wykazały, że właśnie wartość 30 par zasad jest wymagana do uzyskania stabilnego sygnału.'''

primdict={} #sformatowane sekwencje przechowane zostają w słowniku 'primdict'
nwsq=1 #nazwa klucza w nowoutworzonym słowniku 'primdict' (ekwiwalent numeru eksonu lub jednej z jego częsci)
olsq=1 #nazwa klucza w słowniku niesformatowanych sekwencji 'rawexon' (ekwiwalent numeru eksonu)
nrpt=8 #wielkość sekwencji powtórzeń nukleotydowych, wykrywanych przez program (założono, że wartością odcięcia jest 8)
for seqdict in rawexon.values():
	capitalcount=0 #licznik dużych liter, oznaczających kodujący fragment eksonu (jest to częsć szczególnie istotna klinicznie w badaniach genetycznych)
	for x in seqdict:
		if x.isupper():
			capitalcount+=1 #zlicza duże litery dla poszczególnego łańcucha (ich liczba decyduje, czy fragment do analizy będzie dzielony na podfragmenty, czy też pozostanie w dotychczasowym układzie)
	if nwsq in seqexo or allflag == 1: #przetwarzanie fragmentu tylko w przypadku, gdy użytkownik zażądał analizy konkretnie tego eksonu, lub wszystkich eksonów kodujących w genie
		if capitalcount > 600: #zachowanie dla zbyt dużych (>600pz) eksonów, by możliwe było zaprojektowanie primerów wydajnych na całej długości łańcucha DNA		
			over600=input('\n\n--- UWAGA! ---\n\nEkson %s przekroczył długość dla jakiej możliwe jest zaprojektowanie wydajnych primerów. Czy mimo to chcesz je wyszukać? [wpisz T dla tak, lub N dla nie]:\n' % olsq)
			if over600 == 'T' or over600 == 't': #zgoda użytkownika na zaprojektowanie primerów dla bardzo długiego eksonu
				d1=(capitalcount/3)+150 #wyznacza indeks łańcucha w jednej trzeciej eksonu
				d2=2*(capitalcount/3)+150 #wyznacza indeks łańcucha w dwóch trzecich eksonu
				rtbrdr1=int(d1+150) #wyznaczenie prawej granicy pierwszego z trzech fragmentów z zapasem 150pz
				lfbrdr1=int(d1-150) #wyznaczenie lewej granicy drugiego z trzech fragmentów z zapasem 150pz
				rtbrdr2=int(d2+150) #wyznaczenie prawej granicy drugiego z trzech fragmentów z zapasem 150pz
				lfbrdr3=int(d2-150) #wyznaczenie lewej granicy trzeciego z trzech fragmentów z zapasem 150pz
				onehalf=seqdict[:rtbrdr1] #podzielenie sekwencji na pierwszą część
				sechalf=seqdict[lfbrdr1:rtbrdr2] #podzielenie sekwencji na drugą część
				thirdhalf=seqdict[lfbrdr3:] #podzielenie sekwencji na trzecią część
				partA=onehalf[:120]+'['+onehalf[120:] #wstawienie symbolu '[' w pierwszej części
				partA=partA[:-120]+']'+partA[-120:] #wstawienie symbolu ']' w pierwszej części (pozostaje 30pz ze 150pz dodanych do pierwszej połowy po prawej stronie sekwencji)
				partA=excluderepetitions(partA) #eliminacja 'nrpt'-razowych powtórzeń nukleotydowych w sekwencji eksonów
				partB=sechalf[:120]+'['+sechalf[120:] #wstawienie symbolu '[' w drugiej części
				partB=partB[:-120]+']'+partB[-120:] #wstawienie symbolu ']' w drugiej części
				partB=excluderepetitions(partB) #eliminacja 'nrpt'-razowych powtórzeń nukleotydowych w sekwencji eksonów
				partC=thirdhalf[:120]+'['+thirdhalf[120:] #wstawienie symbolu '[' w trzeciej częsci
				partC=partC[:-120]+']'+partC[-120:] #wstawienie symbolu ']' w trzeciej częsci
				partC=excluderepetitions(partC) #eliminacja 'nrpt'-razowych powtórzeń nukleotydowych w sekwencji eksonów
				ky1=str(nwsq)+'A' #uwaga! do klucza trzeba później odnosić się jak do łańcucha znaków- nie jak do liczby
				ky2=str(nwsq)+'B' #uwaga! do klucza trzeba później odnosić się jak do łańcucha znaków- nie jak do liczby
				ky3=str(nwsq)+'C' #uwaga! do klucza trzeba później odnosić się jak do łańcucha znaków- nie jak do liczby
				primdict[ky1]=partA
				primdict[ky2]=partB 
				primdict[ky3]=partC #dodanie danego eksonu do słownika w trzech podzielonych fragmentach- A, B i C
				print('\nDla jednej ze wskazanych sekwencji kodujących (ekson %s) wymagane było podzielenie na trzy części ze względu na ryzyko niepowodzenia reakcji sekwencjonowania na końcowych odcinkach eksonu.\n' % olsq)
				nwsq+=1 #przejście do kolejnego numeru eksonu w słowniku sformatowanych sekwencji
				olsq+=1 #przejście do kolejnego numeru eksonu w słowniku niesformatowanych sekwencji	
			else: #rezygnacja użytkownika z projektowania primerów dla bardzo długiego eksonu
				nwsq+=1 #przejście do kolejnego numeru eksonu w słowniku sformatowanych sekwencji
				olsq+=1 #przejście do kolejnego numeru eksonu w słowniku niesformatowanych sekwencji
		elif capitalcount > 400 and capitalcount <=600: #zachowanie dla bardzo dużych (400-600pz) eksonów
			d1=(capitalcount/3)+150 #wyznacza indeks łańcucha w jednej trzeciej eksonu
			d2=2*(capitalcount/3)+150 #wyznacza indeks łańcucha w dwóch trzecich eksonu
			rtbrdr1=int(d1+150) #wyznaczenie prawej granicy pierwszego z trzech fragmentów z zapasem 150pz
			lfbrdr1=int(d1-150) #wyznaczenie lewej granicy drugiego z trzech fragmentów z zapasem 150pz
			rtbrdr2=int(d2+150) #wyznaczenie prawej granicy drugiego z trzech fragmentów z zapasem 150pz
			lfbrdr3=int(d2-150) #wyznaczenie lewej granicy trzeciego z trzech fragmentów z zapasem 150pz
			onehalf=seqdict[:rtbrdr1] #podzielenie sekwencji na pierwszą część
			sechalf=seqdict[lfbrdr1:rtbrdr2] #podzielenie sekwencji na drugą część
			thirdhalf=seqdict[lfbrdr3:] #OK    podzielenie sekwencji na trzecią część
			partA=onehalf[:120]+'['+onehalf[120:] #wstawienie symbolu '[' w pierwszej częsci
			partA=partA[:-120]+']'+partA[-120:] #wstawienie symbolu ']' w pierwszej częsci (pozostaje 30pz ze 150pz dodanych do pierwszej połowy po prawej stronie sekwencji)
			partA=excluderepetitions(partA) #eliminacja 'nrpt'-razowych powtórzeń nukleotydowych w sekwencji eksonów
			partB=sechalf[:120]+'['+sechalf[120:] #wstawienie symbolu '[' w drugiej częsci
			partB=partB[:-120]+']'+partB[-120:] #wstawienie symbolu ']' w drugiej częsci
			partB=excluderepetitions(partB) #eliminacja 'nrpt'-razowych powtórzeń nukleotydowych w sekwencji eksonów
			partC=thirdhalf[:120]+'['+thirdhalf[120:] #wstawienie symbolu '[' w trzeciej częsci
			partC=partC[:-120]+']'+partC[-120:] #wstawienie symbolu ']' w trzeciej częsci
			partC=excluderepetitions(partC) #eliminacja 'nrpt'-razowych powtórzeń nukleotydowych w sekwencji eksonów
			ky1=str(nwsq)+'A' #uwaga! do klucza trzeba odnosić się później jak do łańcucha znaków- nie jak do liczby
			ky2=str(nwsq)+'B' #uwaga! do klucza trzeba odnosić się później jak do łańcucha znaków- nie jak do liczby
			ky3=str(nwsq)+'C' #uwaga! do klucza trzeba odnosić się później jak do łańcucha znaków- nie jak do liczby
			primdict[ky1]=partA
			primdict[ky2]=partB 
			primdict[ky3]=partC #dodanie danego eksonu do słownika w trzech podzielonych fragmentach- A, B i C
			print('\nDla jednej ze wskazanych sekwencji kodujących (ekson %s) wymagane było podzielenie na trzy części ze względu na ryzyko niepowodzenia reakcji sekwencjonowania na końcowych odcinkach eksonu.\n' % olsq)
			nwsq+=1 #przejście do kolejnego numeru eksonu w słowniku sformatowanych sekwencji
			olsq+=1 #przejście do kolejnego numeru eksonu w słowniku niesformatowanych sekwencji	
		elif capitalcount > 200 and capitalcount <= 400: #alternatywne zachowanie pętli dla dużych eksonów
			d=(capitalcount/2)+150 #wyznacza indeks łańcucha w połowie eksonu
			rtbrdr1=int(d+150) #wyznaczenie prawej granicy pierwszego z dwóch fragmentów z zapasem 150pz
			lfbrdr1=int(d-150) #wyznaczenie lewej granicy drugiego z dwóch fragmentów z zapasem 150pz
			onehalf=seqdict[:rtbrdr1] #podzielenie sekwencji na pierwszą połowę
			sechalf=seqdict[lfbrdr1:] #podzielenie sekwencji na drugą połowę
			partA=onehalf[:120]+'['+onehalf[120:] #wstawienie symbolu '[' w pierwszej połowie
			partA=partA[:-120]+']'+partA[-120:] #wstawienie symbolu ']' w pierwszej połowie (pozostaje 30pz ze 150pz dodanych do pierwszej połowy po prawej stronie sekwencji)
			partA=excluderepetitions(partA) #eliminacja 'nrpt'-razowych powtórzeń nukleotydowych w sekwencji eksonów
			partB=sechalf[:120]+'['+sechalf[120:] #wstawienie symbolu '[' w drugiej połowie
			partB=partB[:-120]+']'+partB[-120:] #wstawienie symbolu ']' w drugiej połowie
			partB=excluderepetitions(partB) #eliminacja 'nrpt'-razowych powtórzeń nukleotydowych w sekwencji eksonów
			ky1=str(nwsq)+'A' #uwaga! do klucza trzeba odnosić się później jak do łańcucha znaków- nie jak do liczby
			ky2=str(nwsq)+'B' #uwaga! do klucza trzeba odnosić się później jak do łańcucha znaków- nie jak do liczby
			primdict[ky1]=partA
			primdict[ky2]=partB #dodanie danego eksonu do słownika w dwóch podzielonych fragmentach- A i B
			print('\nDla jednej ze wskazanych sekwencji kodujących (ekson %s) wymagane było podzielenie na dwie części ze względu na ryzyko niepowodzenia reakcji sekwencjonowania na końcowych odcinkach eksonu.\n' % olsq)
			nwsq+=1 #przejście do kolejnego numeru eksonu w słowniku sformatowanych sekwencji
			olsq+=1 #przejście do kolejnego numeru eksonu w słowniku niesformatowanych sekwencji	
		elif capitalcount <= 200 and capitalcount != 0: #normalne zachowanie dla eksonów poniżej 200pz // wstawienie nawiasów klamrowych do określenia iterseującego nas regionu dla programu primer 3.0/ primer 3 plus
			primexon=rawexon[olsq][:120]+'['+rawexon[olsq][120:] #wstawienie symbolu '['
			primexon=primexon[:-120]+']'+primexon[-120:] #wstawienie symbolu ']'
			primexon=excluderepetitions(primexon) #eliminacja 'nrpt'-razowych powtórzeń nukleotydowych w sekwencji eksonów 
			primdict[nwsq]=primexon #dodanie pod kluczem nwsq (nwsq == nr eksonu) sekwencji z oznaczonym miejscem dla zaprojektowania primerów do słownika, używanego później w programie primer 3.0/ primer 3 plus
			nwsq+=1 #przejście do kolejnego numeru eksonu w słowniku sformatowanych sekwencji
			olsq+=1 #przejście do kolejnego numeru eksonu w słowniku niesformatowanych sekwencji	
		else: #zachowanie pętli przy napotkaniu rekordu FASTA niezawierającego kodującego eksonu (capitalcount == 0) aby zachować prawidłową numerację kolejnych eksonów (kodujących)
			print('\nW sekwencji genu %s ekson numer %s jest eksonem niekodującym. Primery nie zostaną zaprojektowane dla tego regionu.\n' %(req,nwsq))
			nwsq+=1 #przejście do kolejnego numeru eksonu w słowniku sformatowanych sekwencji
			olsq+=1 #przejście do kolejnego numeru eksonu w słowniku niesformatowanych sekwencji
	else: #niepodejmowanie analizy dla eksonu, którego użytkownik nie zażądał
		nwsq+=1 #przejście do kolejnego numeru eksonu w słowniku sformatowanych sekwencji
		olsq+=1 #przejście do kolejnego numeru eksonu w słowniku niesformatowanych sekwencji
#zakończenie tworzenia słownika sformatowanych sekwencji eksonów 'primdict' i wyjście z pętli

if verifyflag == 1: #wykonywane tylko jeżeli użytkownik zażądał weryfikacji sekwencji primerów
	print('\n'+'-'*30+'\nTrwa przetwarzanie danych na temat zmienności populacyjnych w sekwencji genu...\n[Odśwież okno przeglądarki gdy czas oczekiwania na załadowanie treści wynosi powyżej 3 minut]\n')
	driver.get('http://gnomad-beta.broadinstitute.org/') #przejście do bazy danych na temat zmienności populacyjnych w genomie
	WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "home-searchbox-input")))
	elem21 = driver.find_element_by_id("home-searchbox-input") #znalezienie okna wyszukiwania
	elem21.clear()
	assert enst, '\n\nNIE WYKRYTO OZNACZENIA ENST DLA POSZUKIWANEGO GENU. WERYFIKACJA POLIMORFIZMÓW NIE JEST MOŻLIWA.'
	elem21.send_keys(enst) #wprowadzenie nazwy genu po upewnieniu się, że nazwa w formacie ENST została znaleziona na poprzednich etapach
	elem21.send_keys(Keys.RETURN)
	try:
		WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "inner_graph")))
	except TimeoutException:
		driver.refresh() #gdy beza danych ma problem z załadowaniem zawartości, dochodzi do odświeżenia źródła
	else:
		elem22=driver.find_element_by_xpath("//input[@type='checkbox'][@id='filtered_checkbox']")
		if not elem22.get_property('checked'):
			driver2.click(elem22).perform() #zaznaczenie wyszukiwania wszystkich polimorfizmów, dostępnych w bazie danych
			driver2.reset_actions()
		gnomadsrc=driver.page_source
		gnomadcutpoint=gnomadsrc.find('<tr class="table_variant" id="variant_') #znajduje w źródle strony fragment, od którego rozpoczynają się interesujące nas informacje o polimorfizmach
		gnomadsrc=gnomadsrc[gnomadcutpoint:] #odcina wszystkie znaki poprzedzające 'gnomadcutpoint', co zmniejsza rozmiar źródła strony i znacząco przyspiesza późniejsze wyszukiwanie koordynatów zmienności
	print('Zakończono przetwarzanie.\n'+'-'*30+'\n')

#ropoczęcie interakcji z programem Primer 3.0/Plus
try:
	driver.get('https://primer3plus.com/cgi-bin/dev/primer3plus.cgi') #próba połączenia z narzędziem Primer 3 Plus
	elementx=WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "sequenceTextarea"))) #odczekanie do 2 sekund aż pojawi się klikalny przycisk Pick Primers, co świadczyłoby o załadowaniu strony, lub w przeciwnym razie zgłoszenie wyjątku Timeout Exception
except TimeoutException: #zachowanie programu gdy połączenie z Primer 3 Plus się nie powiedzie (Wykorzystanie Primer3Plus)
	print ("\nWystąpił błąd podczas połączenia z narzędziem Primer 3 Plus. Do zaprojektowania primerów zostanie wykorzystany Primer3.0.\n")
	for (key, prsq) in primdict.items(): #przeszukanie słownika numerów eksonów i ich sformatowanych sekwencji (ze wstawionymi nawiasami klamrowymi i wyłączonymi powtórzeniami nukleotydowymi)
		keyfull=key #pełna nazwa fragmentu eksonu (nawet podzielonego na kilka części), w celu późniejszego wyświetlenia w ramach informacji dla użytkownika
		if allflag == 0: #werfikacja, czy użytkownik nie zażądał zaprojektowania wszystkich CDS	
			if type(key)==str: #zachowanie pętli dla wybranych, podzielonych na kilka części eksonów
				key=key[:-1] #odcięcie litery od numeru eksonu
				nkey=int(key) #przekształcienie reszty łańcucha znaków na liczbę
				if nkey in seqexo: #część wykonywana tylko jeżeli ekson jest na liście przez nas wybranych
					primer3search() #wyszukiwanie sekwencji primerów w programie Primer 3.0
			else: #zachowanie pętli dla wybranych, niepodzielonych eksonów 
				if key in seqexo: #część wykonywana tylko jeżeli ekson jest na liście przez nas wybranych
					primer3search() #wyszukiwanie sekwencji primerów w programie Primer 3.0
		else: #zachowanie pętli jeżeli użytkownik zażądał zaprojektowania primerów do wszystkich CDS
			primer3search() #wyszukiwanie sekwencji primerów w programie Primer 3.0
else: #zachowanie programu gdy połączenie z Primer 3 Plus się powiedzie
	for (key, prsq) in primdict.items(): #przeszukanie słownika numerów eksonów i ich sekwencji ze wstawionymi nawiasami klamrowymi
		keyfull=key #pełna nazwa fragmentu eksonu (nawet podzielonego na kilka części), w celu późniejszego wyświetlenia w ramach informacji dla użytkownika
		if allflag == 0: #werfikacja, czy użytkownik nie zażądał zaprojektowania wszystkich CDS		
			if type(key)==str: #zachowanie pętli dla wybranych, podzielonych na kilka części eksonów
				key=key[:-1] #odcięcie litery od numeru eksonu
				nkey=int(key) #przekształcienie reszty łańcucha znaków na liczbę
				if nkey in seqexo: #część wykonywana tylko jeżeli ekson jest na liście przez nas wybranych
					primer3plussearch() #wyszukiwanie sekwencji primerów w programie Primer 3 Plus
			else: #zachowanie pętli dla wybranych, niepodzielonych eksonów  
				if key in seqexo: #część wykonywana tylko jeżeli ekson jest na liście przez nas wybranych
					primer3plussearch() #wyszukiwanie sekwencji primerów w programie Primer 3 Plus
		else: #zachowanie pętli jeżeli użytkownik zażądał zaprojektowania primerów do wszystkich CDS
			primer3plussearch() #wyszukiwanie sekwencji primerów w programie Primer 3 Plus		
#zakończenie interakcji z programem primer 3.0/Plus

print('\n\n'+'-'*30+'\nUdało się odnaleźć powyższe sekwencje primerów dla wersji %s genu %s' %(seqver,req))

driver.quit() #zamyka przeglądarkę po wykonaniu zadania
