// Menüü struktuuri konfiguratsioon
const NAV_CATEGORIES = [
  {
    name: 'Tähendused',
    cards: [
      { name: 'Sõnavõrgustik', desc: 'Liigu mööda tähendustevahelisi seoseid ja vaata, kuhu sedasi sattuda võib.', href: '../sonavorgustik/index.html' },
      { name: 'Polüseemia', desc: 'Sõnad reastatud tähenduste arvu järgi.', href: '../polüseemia/index.html' },
      { name: 'Lühiühendus', desc: 'Leia tähendustevahelisi seoseid pidi liikudes lühim tee ühest sõnast teiseni.', href: '../lyhiühendus/index.html' },
      { name: 'Registrimaatriks', desc: 'Registrimärgendiga sõnad.', href: '../registrimaatriks/index.html' },
      { name: 'Sünonüümitihedus', desc: 'Sünonüümid on eri sõnad, mis on sama tähendusega.', href: '../sünonüümid/index.html' },
      { name: 'Fraseoloogilised väljendid', desc: 'Uurige 1500+ fraseoloogiliste väljendite semantiliste kategooriate võrgustikku.', href: '../fraseoloogilised/index.html' },
      { name: 'Kaashüponüümid', desc: 'Sõnad mis jagavad sama ülemmõistet — kaashüponüümide klastrid.', href: '../kaashüponüümid/index.html' },
      { name: 'Antonüümid', desc: 'Vastupidise tähendusega sõnad.', href: '../antonüümid/index.html' },
    ]
  },
  {
    name: 'Liitsõnad',
    cards: [
      { name: 'Produktiivsed liitujad', desc: 'Millised sõnad moodustavad kõige rohkem liitsõnu?', href: '../produktiivsus/index.html' },
      { name: 'Liitsõnade sügavus', desc: 'Kui liitsõna koosneb teistest liitsõnadest.', href: '../sügavus/index.html' },
    ]
  },
  {
    name: 'Sõnade tähed',
    cards: [
      { name: 'Palindroomid', desc: 'Sõnad, mis tagurpidi loetuna annavad sama sõna.', href: '../palindroomid/index.html' },
      { name: 'Anagrammipaarid', desc: 'Samad tähed, eri sõnad.', href: '../anagrammid/index.html' },
      { name: 'Anadroomid', desc: 'Ühtepidi üks sõna, teistpidi teine sõna.', href: '../anadroomid/index.html' },
      { name: 'Minimaalpaarid', desc: 'Sõnapaarid mis erinevad täpselt ühe tähe poolest.', href: '../minimaalpaarid/index.html' },
      { name: 'Ainult täishäälikud', desc: 'Sõnad mis koosnevad üksnes täishäälikutest', href: '../täishäälikud/index.html' },
      { name: 'Reduplikatsioonid', desc: 'Sõnad kus esimene pool kordab teist poolt', href: '../reduplikatsioonid/index.html' },
      { name: 'Kärpimisahelad', desc: 'Sõnad, mille esimese tähe eemaldamisel tekib uus sõna.', href: '../kärpimine/index.html' },
      { name: 'Scrabble', desc: 'Millised eestikeelsed sõnad toovad Scrabble\'is kõige rohkem punkte?', href: '../scrabble/index.html' },
    ]
  }
];
