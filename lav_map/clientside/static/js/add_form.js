ymaps.ready(init);
    var myMap;

    var x;
    var y;

    function init() {
        myMap = new ymaps.Map("map", {
            center: [53.902284, 27.561831],
            zoom: 11
        }, {
            balloonMaxWidth: 200,
            searchControlProvider: 'yandex#search'
        });

        // Обработка события, возникающего при щелчке
        // левой кнопкой мыши в любой точке карты.
        // При возникновении такого события откроем балун.

        var myPlacemark = null;
        myMap.events.add('click', function (e) {

            var in_x = document.getElementById('id_x');
            var in_y = document.getElementById('id_y');

            var coords = e.get('coords');
            if (myPlacemark) {
                myMap.geoObjects.remove(myPlacemark);
            }
            myPlacemark = new ymaps.Placemark(coords, {}, {
                iconLayout: 'default#image',
                iconImageHref: STATIC_URL + 'media/point.png',
                iconImageSize: [30, 30],
                iconImageOffset: [-15, -30]
            });
            myMap.geoObjects.add(myPlacemark);
            in_x.value = coords[0].toPrecision(8);
            in_y.value = coords[1].toPrecision(8);
        });

        // Обработка события, возникающего при щелчке
        // правой кнопки мыши в любой точке карты.
        // При возникновении такого события покажем всплывающую подсказку
        // в точке щелчка.
        //myMap.events.add('contextmenu', function (e) {
            //myMap.hint.open(e.get('coords'), 'Кто-то щелкнул правой кнопкой');
        //});

        // Скрываем хинт при открытии балуна.
        //myMap.events.add('balloonopen', function (e) {
            //myMap.hint.close();
        //});
    }