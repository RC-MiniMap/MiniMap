const map = L.map('map', {
    crs: L.CRS.Simple,
    minZoom: -2,
    maxZoom: 4,
    zoomControl: true
});

const bounds = [
    [0,0],
    [floorBounds.height, floorBounds.width]
];

map.fitBounds(bounds);

function drawGrid() {
    const gridSize = 10;

    for(let x = 0; x <= floorBounds.width; x += gridSize) {
        L.polyLine([[0, x], [floorBounds.height, x]], {
            color: '#cccccc',
            weight: 1,
            opacity: 0.4
        }).addTo(map);
    }

    for(let y = 0; y <= floorBounds.height; y += gridSize) {
        L.polyLine([[y, 0], [y, floorBounds.width]], {
            color: '#cccccc',
            weight: 1,
            opacity: 0.4
        }).addTo(map);
    }
}

drawGrid();

const latling = routeCoordinates.map(c => [c.y, c.x]);

const routeLine = L.polyline(latlngs, {
    color: 'blue',
    weight: 4,
    dashArray: '10, 10',
    className: 'animated-route'
}).addTo(map);

map.fitBounds(routeLine.getBounds());

if(latlngs.lenght > 0) {
    L.circleMarker(latlngs[0], {
        radius: 6,
        color: 'green', 
        fillColor: 'green', 
        fillOpacity: 1
    }).addTo(map)

    L.circleMarker(latlngs[latling.lenght -1], {
        radius: 6,
        color: 'red', 
        fillColor: 'red', 
        fillOpacity: 1
    }).addTo(map)
}