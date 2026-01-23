  const searchInput = document.getElementById('searchInput');
  const voiceBtn= document.getElementById('voiceBtn');
  const fileInput = document.getElementById('fileInput');
  const linkBtn = document.getElementById('linkBtn');
  const sendBtn = document.getElementById('sendBtn');
  const preview = document.getElementById('preview');

  // le vocale
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang ='fr-FR';

    voiceBtn.addEventListener('click', () => {
      recognition.start();
    });

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      searchInput.value = transcript;
    };
  } else {
    voiceBtn.disabled = true;
    voiceBtn.title = "Votre navigateur ne supporte pas la reconnaissance vocale";
  }
  
  // Stockage temporaire des fichiers et liens
  const filesArray = [];
  const linksArray = [];

  // Gestion fichier/image
  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if(file) {
      filesArray.push(file);
      alert(`Fichier ajouté: ${file.name}`);
    }
    fileInput.value = '';
  });

  // Gestion lien
  linkBtn.addEventListener('click', () => {
    const url = prompt("Entrez le lien URL:");
    if(url) {
      linksArray.push(url);
      alert(`Lien ajouté: ${url}`);
    }
  });

  // Bouton Envoyer
  sendBtn.addEventListener('click', () => {
    // Texte
    const textValue = searchInput.value.trim();
    if(textValue) {
      const div = document.createElement('div');
      div.textContent = 'Texte: ' + textValue;
      preview.appendChild(div);
      searchInput.value = '';
    }

    // Fichiers
    filesArray.forEach(file => {
      const div = document.createElement('div');
      if(file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        div.appendChild(img);
        div.appendChild(document.createTextNode(' ' + file.name));
      } else {
        div.textContent = 'Fichier: ' + file.name;
      }
      preview.appendChild(div);
    });
    filesArray.length = 0;

    // Liens
    linksArray.forEach(url => {
      const div = document.createElement('div');
      const a = document.createElement('a');
      a.href = url;
      a.textContent = url;
      a.target = "_blank";
      div.appendChild(a);
      preview.appendChild(div);
    });
    linksArray.length = 0;
  });