let animeContainer = document.querySelector('.anime-container');

// Variable pour contrôler la vitesse du défilement
let scrollSpeed = 0;
let scrollInterval;

// Fonction pour démarrer le défilement automatique
function startScrolling(direction) {
    if (scrollInterval) {
        clearInterval(scrollInterval);  // Efface tout intervalle précédent
    }

    // Démarre le défilement en continu dans la direction choisie
    scrollInterval = setInterval(() => {
        animeContainer.scrollBy({
            left: direction * 100,  // Décale de 100px à chaque intervalle pour un défilement plus rapide
            behavior: 'smooth'
        });
    }, 5);  // Défilement toutes les 5ms pour plus de réactivité
}

// Fonction pour arrêter le défilement
function stopScrolling() {
    if (scrollInterval) {
        clearInterval(scrollInterval);  // Arrête l'intervalle de défilement
    }
}

// Événement de mouvement de la souris
animeContainer.addEventListener('mousemove', function(event) {
    // Récupère la position du curseur dans le conteneur
    let containerRect = animeContainer.getBoundingClientRect();
    let cursorPosition = event.clientX - containerRect.left;

    // Largeur du conteneur
    let containerWidth = animeContainer.offsetWidth;

    // Si le curseur est proche du bord droit
    if (cursorPosition > containerWidth * 0.8) {
        scrollSpeed = 4;  // Défile vers la droite
        startScrolling(scrollSpeed);
    }
    // Si le curseur est proche du bord gauche
    else if (cursorPosition < containerWidth * 0.8) {
        scrollSpeed = -4;  // Défile vers la gauche
        startScrolling(scrollSpeed);
    }
    else {
        stopScrolling();  // Arrête le défilement si le curseur n'est pas près des bords
    }
});

// Arrête le défilement dès que la souris quitte le conteneur
animeContainer.addEventListener('mouseleave', function() {
    stopScrolling();
});

// Gestion dynamique de la soumission du formulaire
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function (event) {
            event.preventDefault(); // Empêche le rechargement de la page

            let formData = new FormData(this);
            let actionUrl = this.getAttribute("action");

            fetch(actionUrl, {
                method: "POST",
                body: formData
            })
            .then(response => response.json()) // Attend une réponse JSON
            .then(data => {
                if (data.error) {
                    alert(data.error); // Affiche un message d'erreur si nécessaire
                } else {
                    document.querySelector("#anime_list").innerHTML = data.html; // Met à jour la liste des animes
                }
            })
            .catch(error => console.error("Erreur :", error));
        });
    });
});
