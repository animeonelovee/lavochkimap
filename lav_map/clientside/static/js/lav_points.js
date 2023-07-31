ymaps.ready(init);
    function init(){

        var myMap = new ymaps.Map("map", {
                center: [53.902287, 27.561824],
                zoom: 12
            }, {
                searchControlProvider: 'yandex#search'
            }), 
            objectManager = new ymaps.ObjectManager({
                clusterize: true,
                gridSize: 64,
                clusterOpenBalloonOnClick: false
            });

        objectManager.objects.options.set({
            iconLayout: 'default#image',
            iconImageHref: STATIC_URL + 'media/point.png',
            iconImageSize: [30, 30],
            iconImageOffset: [-15, -30]
        });


        objectManager.clusters.options.set({
            clusterIcons: [{
                href: STATIC_URL + 'media/cluster.png',
                size: [40, 40],
                offset: [-20, -20],
            }]
        });

        myMap.geoObjects.add(objectManager);
        
        // Создадим 5 пунктов выпадающего списка.
        var listBoxItems = ['Спинка', 'Тень', 'Падик']
                .map(function (title) {
                    return new ymaps.control.ListBoxItem({
                        data: {
                            content: title
                        },
                        state: {
                            selected: false
                        }
                    })
                }),
            reducer = function (filters, filter) {
                filters[filter.data.get('content')] = filter.isSelected();
                return filters;
            },
            // Теперь создадим список, содержащий 5 пунктов.
            listBoxControl = new ymaps.control.ListBox({
                data: {
                    content: 'Фильтр',
                    title: 'Фильтр'
                },
                items: listBoxItems,
                state: {
                    // Признак, развернут ли список.
                    expanded: true,
                    filters: listBoxItems.reduce(reducer, {})
                }
            });
        myMap.controls.add(listBoxControl);

        // Добавим отслеживание изменения признака, выбран ли пункт списка.
        listBoxControl.events.add(['select', 'deselect'], function (e) {
            var listBoxItem = e.get('target');
            var filters = ymaps.util.extend({}, listBoxControl.state.get('filters'));
            filters[listBoxItem.data.get('content')] = listBoxItem.isSelected();
            ItemContent = listBoxItem.data.get('content')
            listBoxControl.state.set('filters', filters);
            return ItemContent
        });

        var filterMonitor = new ymaps.Monitor(listBoxControl.state);
        filterMonitor.add('filters', function (filters) {
            // Применим фильтр.
            dictionary = {'Спинка': false, 'Тень': false, 'Падик': false}
            objectManager.setFilter(getFilterFunction(filters));

        });

        function getFilterFunction(categories) {
            return function (obj) {

                for (let key in categories) {
                    if (categories[key] == true){
                        x = obj.properties.balloonContent[key] != false
                    }
                    else{
                        x = true 
                    }
                    dictionary[key] = x
                }
                return (dictionary['Спинка'] !=0 || dictionary['Тень'] !=0 || dictionary['Падик'] !=0) && (dictionary['Спинка'] == dictionary['Тень'] && dictionary['Тень'] == dictionary['Падик'])

            }
        }


        $.ajax({
            url: "/api/points/"
        }).done(function(data) {
            objectManager.add(data);
        });

    }