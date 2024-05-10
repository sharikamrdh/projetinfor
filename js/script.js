let menu= document.querySelector('#menu-icon');
let navlist = document.querySelector('.navlist');
menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navlist.classList.toggle('open');
};

const sr = ScrollReveal ({
    distance: '65px',
    duration: 2600,
    delay: 450,
    reset: true
});

sr.reveal('.container', {delay:200, origin:'top'});

// Fonction pour afficher la barre de progression
function showProgressBar() {
    document.getElementById('progress-bar').style.display = 'block';
}

// Fonction pour masquer la barre de progression
function hideProgressBar() {
    document.getElementById('progress-bar').style.display = 'none';
}

// Fonction pour compresser un fichier
function compressFile() {
    // Afficher la barre de progression au début de la compression
    showProgressBar();

    // Récupérer le chemin du fichier à compresser depuis le formulaire
    let filePath = document.getElementById('file_path').value;

    // Envoyer une requête POST au serveur pour compresser le fichier
    fetch('/compress', {
        method: 'POST',
        body: JSON.stringify({ file_path: filePath }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Masquer la barre de progression une fois la compression terminée
        hideProgressBar();
        return response.json();
    })
    .then(data => {
        // Afficher les données de compression dans la console
        console.log(data);
        // Rediriger vers la page de rapport de compression
        window.location.href = '/compression_report';
    })
    .catch(error => {
        console.error('There was a problem with the compression operation:', error);
        // Masquer la barre de progression en cas d'erreur
        hideProgressBar();
    });
}

// Fonction pour décompresser un fichier
function decompressFile() {
    // Afficher la barre de progression au début de la décompression
    showProgressBar();

    // Récupérer le chemin du fichier à décompresser depuis le formulaire
    let filePath = document.getElementById('decompress_file_path').value;

    // Envoyer une requête POST au serveur pour décompresser le fichier
    fetch('/decompress', {
        method: 'POST',
        body: JSON.stringify({ file_path: filePath }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Masquer la barre de progression une fois la décompression terminée
        hideProgressBar();
        return response.json();
    })
    .then(data => {
        // Afficher les données de décompression dans la console
        console.log(data);
        // Rediriger vers la page de rapport de décompression
        window.location.href = '/decompression_report';
    })
    .catch(error => {
        console.error('There was a problem with the decompression operation:', error);
        // Masquer la barre de progression en cas d'erreur
        hideProgressBar();
    });
}

