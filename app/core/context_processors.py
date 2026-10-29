def global_partners(request):
    partners_list = [
        {
            "name": "AllCycles",
            "url": "https://allcycles.fr/",
            "description": "Partenaire historique et technique de notre structure, le magasin ALLCYCLES est bien plus qu’un soutien : c’est un véritable repère pour les passionnés de vélo à Meaux. Grâce à une sélection rigoureuse de matériels de pointe, un atelier de précision et des conseils d'experts adaptés à toutes les pratiques – de la route au haut niveau –, ALLCYCLES accompagne au quotidien nos coureurs de la Division Nationale 3 jusqu'à l'école de vélo. Cette collaboration étroite garantit à nos athlètes de disposer du meilleur équipement pour exprimer tout leur potentiel sur les routes de France.",
            "image": "img/partners/stores/allcycles.jpeg",
            "logo": "img/partners/logos/allcycles.png",
        },
        {
            "name": "Ville de Meaux",
            "url": "https://www.ville-meaux.fr/",
            "description": "Ancrée dans l’histoire sportive locale, la Ville de Meaux apporte un soutien institutionnel et logistique indispensable au développement du club. En accompagnant notre équipe de Division Nationale 3 et l'ensemble de notre école de formation, la municipalité contribue activement au dynamisme du territoire et au rayonnement de nos couleurs bien au-delà de la Seine-et-Marne. Un partenariat fort, fondé sur des valeurs communes d'effort, de cohésion et d'ambition pour tous les sportifs meldois.",
            "image": "img/partners/stores/meaux.jpg",
            "logo": "img/partners/logos/meaux.png",
        },
        {
            "name": "Leclerc Meaux",
            "url": "https://www.e.leclerc/mag/e-leclerc-meaux?srsltid=AYCX9vLDJWXCjI4PWI6Rp1BTW6BbXHjzHRyoHCA3cdW1fkXQaKvVo9ip",
            "description": "Acteur économique incontournable de la vie locale, Leclerc Meaux apporte un soutien précieux et engagé au développement de notre club. En s’associant à notre équipe de Division Nationale 3 et à notre école de formation, cette enseigne de proximité témoigne d’un attachement fort au dynamisme de notre territoire et au sport pour tous. Un partenariat de confiance, fondé sur des valeurs de partage, de dynamisme et d'accompagnement de la jeunesse meldoise sur la route de la réussite.",
            "image": "img/partners/stores/leclerc.jpg",
            "logo": "img/partners/logos/leclerc.png",
        },
        {
            "name": "Hyundai Protea by riester",
            "url": "https://www.riester.fr/concession/hyundai%20meaux",
            "description": "Partenaire incontournable de la mobilité du club, Hyundai Protea By Riester garantit à nos coureurs et à notre encadrement des déplacements sécurisés et confortables sur toutes les épreuves de la saison. En mettant à disposition une flotte de véhicules adaptée aux exigences du haut niveau, le groupe Riester joue un rôle clé dans la logistique de notre équipe de Division Nationale 3. Un partenariat stratégique et de confiance, fondé sur l'excellence, l'innovation et l'ambition partagée de faire briller le Team AllCycles Meaux aux quatre coins de la France.",
            "image": "img/partners/stores/hyundai.jpeg",
            "logo": "img/partners/logos/hyundai.png",
        },
        {
            "name": "Sena cycling",
            "url": "https://www.sena.com/fr/product/cycling/",
            "description": "Partenaire incontournable de la mobilité du club, Hyundai Protea By Riester garantit à nos coureurs et à notre encadrement des déplacements sécurisés et confortables sur toutes les épreuves de la saison. En mettant à disposition une flotte de véhicules adaptée aux exigences du haut niveau, le groupe Riester joue un rôle clé dans la logistique de notre équipe de Division Nationale 3. Un partenariat stratégique et de confiance, fondé sur l'excellence, l'innovation et l'ambition partagée de faire briller le Team AllCycles Meaux aux quatre coins de la France.",
            "image": "img/partners/stores/sena.jpg",
            "logo": "img/partners/logos/sena.png",
        },
        {
            "name": "Mauro Ribeiro",
            "url": "https://mauroribeirosports.com.br/",
            "description": "Concepteur de nos tenues officielles, Mauro Ribeiro habille avec brio l'ensemble du Team AllCycles Meaux. En nous fournissant des équipements textiles haut de gamme qui associent design soigné, confort absolu et performances aérodynamiques, la marque permet à nos coureurs de porter fièrement nos couleurs sur toutes les routes de France — de l'école de vélo jusqu'au plus haut niveau de la Division Nationale 3. Un partenariat d'exception pour rouler avec style, cohésion et ambition.",
            "image": "img/partners/stores/mauro.png",
            "logo": "img/partners/logos/allcycles.png",
        },
        {
            "name": "CCVP",
            "url": "https://ccvp.wearetaka.com/",
            "description": "Spécialiste reconnu du génie climatique, CCVP s'associe au Team AllCycles Meaux autour d'une vision commune de l'avenir et de la performance responsable. En plaçant l'efficacité énergétique, l'innovation et la responsabilité sociétale (RSE) au cœur de son métier, CCVP partage naturellement les valeurs de transition écologique et de mobilité douce portées par la pratique du cyclisme. Un soutien précieux pour accompagner le développement de nos coureurs tout en affirmant notre engagement collectif pour un territoire plus durable.",
            "image": "img/partners/stores/ccvp.jpeg",
            "logo": "img/partners/logos/ccvp.png",
        },
    ]

    return {"FOOTER_PARTNERS": partners_list}
