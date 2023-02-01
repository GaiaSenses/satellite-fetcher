window.onload = () => {
  const form = document.querySelector('form');
  const copyBtn = document.getElementById('copy-btn');
  const resultContainer = document.getElementById('result');
  const select = document.getElementById('data-source-select');
  const latitudeInput = document.getElementById('latitude');
  const longitudeInput = document.getElementById('longitude');

  const validateCoord = (lat, lon) => {
    lat = Number(lat)
    lon = Number(lon)
    return lat && lat >= -90.0 && lat <= 90.0 && lon && lon >= -180.0 && lon <= 180.0;
  }

  const handleSubmit = (e) => {
    e.preventDefault();

    const dataSource = select.selectedOptions[0].value;
    const lat = latitudeInput.value;
    const lon = longitudeInput.value;

    if (!validateCoord(lat, lon)) {
      alert('Coordenadas inválidas! A latitude deve estar entre -90.0 e 90.0 e a Longitude entre -180 e 180');
      latitudeInput.value = '';
      longitudeInput.value = '';
      return;
    }

    resultContainer.innerText = 'carregando...';

    const params = { lat, lon }
    fetch(`${location.origin}/${dataSource}?${new URLSearchParams(params)}`)
      .then((res) => res.json())
      .then((data) => {
        resultContainer.innerText = JSON.stringify(data, null, 2);
      });
  }

  const handleCopy = (e) => {
    const btn = e.target;

    navigator.clipboard
             .writeText(resultContainer.innerText)
             .then(() => {
               btn.className = 'copy-success';
               btn.title = '';

               setTimeout(() => {
                 btn.className = 'copy-icon';
                 btn.title = 'copy';
               }, 2000);
             });
  }

  const createLocationButton = (clickHandler) => {
    const container = form.querySelector('#input-fields-container');

    const div = document.createElement('div');
    div.className = 'input-field';

    const btn = document.createElement('button');
    btn.id = 'my-location-btn';
    btn.textContent = 'Minha Localização';
    btn.addEventListener('click', clickHandler);

    div.appendChild(btn);
    container.appendChild(div);
  }

  const handleLocationButtonClick = (e) => {
    e.preventDefault();

    navigator.geolocation.getCurrentPosition((pos) => {
      latitudeInput.value = pos.coords.latitude;
      longitudeInput.value = pos.coords.longitude;
    }, (err) => {
      let msg = '';
      if (err.code === GeolocationPositionError.PERMISSION_DENIED) {
        msg = 'Permissão negada para acessar localização';
      }
      else if (err.code === GeolocationPositionError.POSITION_UNAVAILABLE) {
        msg = 'Localização indisponível';
      }
      else if (err.code === GeolocationPositionError.TIMEOUT) {
        msg = 'Tempo limite alcançado';
      }
      else {
        msg = err.message;
      }
      alert(msg);
    });
  }

  if (navigator.geolocation) {
    createLocationButton(handleLocationButtonClick);
  }

  form.addEventListener('submit', handleSubmit);
  copyBtn.addEventListener('click', handleCopy);
}
