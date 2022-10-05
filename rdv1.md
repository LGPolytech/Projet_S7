# RDV 1

- Modèle bicyclette (faute) : 2 roues 

Réseau de neurone -> modèlise une fonction mathématique 

fct : image vers angle

Méthode : tracer plusieurs trajets, en sélectionner 1 - trajectoire voiture


### Ce qu'il faut faire
- Lire et comprendre le code de l'étudiant
1. Corriger des Bugs (redimensionnement de l'interface graphique, ...)
2. Gestion de plusieurs courbes
        - Vérifier premier point des nouvelles courbes
        - Sauvegarder chaque courbes
3. Mesurer si modèle bicyclette est satisfaisant 
4. Possiblilité d'éditer des circuits


- Nouvelles fonctionalités :
    - Modifier un tracé existant
        - Gommes / Crayon
        - Courbes avec points de contrôle
            - Trouver une lib de gestion de courbes / dessin vectoriel en python
        - Copier/Coller des courbes
        - Génération automatique de courbes "proches mais différentes" (étape aqucisition des données d'apprentissage) $\implies$ Dataset d'apprentissage 

- Evaluation 
    - Numérique / modèle RVIZ
        - Fonctionalité à ajouter - chercher sur RVIZ comment ajouter un dessin qui ne soit pas un obstacle : Superposer au tracé RVIZ la trajectoire qui était la commande
        - Métrique d'évaluation, ressemblance trajectoire désinner dans l'outils d'Antoine VS trajectoire de la voiture simulée
            - Comparée tracé et simultion voiture (erreur de distance entre les deux)
    - Sur le terrain / Physique - DES VRAI ROBOOOTS !!!

- Idées ultérieures : 
    - Limiter le dessin dans un couloir ?
    Ou dessiner des bordures supplémentaires liées à la largeur de la voiture, gestion des stops et autres lignes / dessins non obstacle 

- "Optionnel" apprentissage actif
    - Tracer des circuits au fur et à mesure de l'avancé de la voiture

### Bazar

RVIZ : simulation d'un véhicule en fonction des propriétés particulières (à voir)

Machine virtuelle dans biblio(graphie ?) - tous les packages - la bonne version de Linux

"Il faut charger la tajectoire depuis ce qu'a fais l'étudiant sur RVIZ"


- Tutoriaux : musher.io

username : robot
mdp : prl_robot   (Attention qwerty)

``` 
rostlauch mushr_sim teleop.launch
```

- Particularité de Qt : "fonctionnement par signaux et par slot"
    - "Envoie de signal / Slot : attend un signal" $\implies$ a checker / Comprendre

### Rendu Attendu 

