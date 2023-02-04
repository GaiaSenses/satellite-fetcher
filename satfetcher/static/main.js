window.onload = () => {
  const form = document.querySelector('form');
  const copyBtn = document.getElementById('copy-btn');
  const resultContainer = document.getElementById('result');
  const select = document.getElementById('data-source-select');
  const latitudeInput = document.getElementById('latitude');
  const longitudeInput = document.getElementById('longitude');
  const fieldsContainer = document.getElementById('input-fields-container');
  const distanceContainer = createDistanceContainer();
  const distanceInput = distanceContainer.querySelector('#distance');

  const validateCoord = (lat, lon) => {
    lat = Number(lat)
    lon = Number(lon)
    return lat && lat >= -90.0 && lat <= 90.0 && lon && lon >= -180.0 && lon <= 180.0;
  }

  const validateDist = (dist) => {
    return (dist === '') || (Number(dist) >= 0.0);
  }

  const handleSubmit = (e) => {
    e.preventDefault();

    const dataSource = select.selectedOptions[0].value;
    const lat = latitudeInput.value;
    const lon = longitudeInput.value;
    const dist = distanceInput.value;

    if (!validateCoord(lat, lon)) {
      alert('Coordenadas inválidas! A latitude deve estar entre -90.0 e 90.0 e a Longitude entre -180 e 180');
      latitudeInput.value = '';
      longitudeInput.value = '';
      return;
    }

    if (!validateDist(dist)) {
      alert('Distância inválida! A distância deve ser maior que 0');
      dist.value = '';
      return;
    }

    resultContainer.innerText = 'carregando...';

    const params = dist === '' ? { lat, lon } : { lat, lon, dist };
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

  function createDistanceContainer() {
    const div = document.createElement('div');
    div.className = 'input-field';

    const label = document.createElement('label');
    label.setAttribute('for', 'distance');
    label.textContent = 'Distância Limite (Km): ';

    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'distance';
    input.name = 'distance';

    div.appendChild(label);
    div.appendChild(input);

    return div;
  }

  const createLocationButton = (clickHandler) => {
    const btn = document.createElement('button');
    btn.id = 'my-location-btn';
    btn.className = 'input-field';
    btn.textContent = 'Minha Localização';
    btn.addEventListener('click', clickHandler);

    return btn;
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

  function handleSelect(e) {
    const item = e.target.selectedOptions[0].value;

    if (item !== 'rainfall' && !distanceContainer.parentNode) {
      fieldsContainer.appendChild(distanceContainer);
    }
    else if (item === 'rainfall' && distanceContainer.parentNode) {
      fieldsContainer.removeChild(distanceContainer);
    }
  }

  if (navigator.geolocation) {
    const container = form.querySelector('#buttons-container');
    const btn = createLocationButton(handleLocationButtonClick);
    container.prepend(btn);
  }

  if (select.selectedOptions[0].value !== 'rainfall') {
    fieldsContainer.appendChild(distanceContainer);
  }

  form.addEventListener('submit', handleSubmit);
  copyBtn.addEventListener('click', handleCopy);
  select.addEventListener('change', handleSelect);
}
