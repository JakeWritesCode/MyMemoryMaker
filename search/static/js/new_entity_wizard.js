// Functions for the new entity wizard.
// They need to be here because JS doesn't work very well when you pull it in via fetch


function selectEntityType(typeSelected) {
    // User selects a new entity type, we render the appropriate form and steps.
    let headingText = ""
    let partialToRender = ""
    let callback = null
    if (typeSelected === "activity") {
        headingText = "Describe your activity."
        partialToRender = newActivityURL
        callback = initNewActivityForm
    }
    if (typeSelected === "place") {
        headingText = "Describe your place."
        partialToRender = newPlaceURL
        callback = initNewPlaceForm
    }

    document.getElementById("new-entity-header").innerHTML = headingText
    fetch(partialToRender, {
        method: 'GET',
    })
        .then(response => response.text())
        .then(html => {
                document.getElementById("form-step-target").innerHTML = html;
                if (callback) {
                    callback()
                }
            }
        )
    document.getElementById("preview-container").classList.remove("d-none")
}

function initNewEntityForm() {
    const headline = document.getElementById("id_headline")
    headline.addEventListener("change", function () {
        updatePreviewCard("search-entity-headline", headline.value)
    })
    const priceLower = document.getElementById("id_price_lower")
    priceLower.addEventListener("change", function () {
        updatePreviewCard("search-entity-price-lower", priceLower.value)
    })
    const priceUpper = document.getElementById("id_price_upper")
    priceUpper.addEventListener("change", function () {
        updatePreviewCard("search-entity-price-upper", priceUpper.value)
    })
    const durationLower = document.getElementById("id_duration_lower")
    durationLower.addEventListener("change", function () {
        updatePreviewCard("search-entity-duration-lower", durationLower.value)
    })
    const durationUpper = document.getElementById("id_duration_upper")
    durationUpper.addEventListener("change", function () {
        updatePreviewCard("search-entity-duration-upper", durationUpper.value)
    })
    const peopleLower = document.getElementById("id_people_lower")
    peopleLower.addEventListener("change", function () {
        updatePreviewCard("search-entity-people-lower", peopleLower.value)
    })
    const peopleUpper = document.getElementById("id_people_upper")
    peopleUpper.addEventListener("change", function () {
        updatePreviewCard("search-entity-people-upper", peopleUpper.value)
    })

    // Dynamically render the image that is loaded into the filefield.
    document.getElementById('id_uploaded_image').onchange = function (evt) {
        const tgt = evt.target || window.event.srcElement,
            files = tgt.files;

        // FileReader support
        if (FileReader && files && files.length) {
            var fr = new FileReader();
            fr.onload = function () {
                document.getElementById("search-entity-image").src = fr.result;
            }
            fr.readAsDataURL(files[0]);
        }
    }

    tinymce.init({
        selector: '#id_description',
        menubar: false,
        setup: function (ed) {
            ed.on('change', function (e) {
                updatePreviewCard("search-entity-description", ed.getContent());
            });
        }
    });

    htmx.process(document.body);
}

function initNewActivityForm() {
    initNewEntityForm()
    document.getElementById("")
}

function initNewPlaceForm() {
    initNewEntityForm()
    const input = document.getElementById('id_place_search');
    new mdb.Select(document.getElementById('id_activities'), {"filter": true})

    const options = {
        componentRestrictions: {country: "uk"},
        fields: ["geometry", "name", "url", "photos", "place_id", "price_level", "rating", "formatted_address"],
        strictBounds: false,
    };

    const autocomplete = new google.maps.places.Autocomplete(input, options);
    autocomplete.addListener("place_changed", function () {
        const place = autocomplete.getPlace();
        document.getElementById("id_location_lat").value = place.geometry.location.lat()
        document.getElementById("id_location_long").value = place.geometry.location.lng()
        document.getElementById("id_headline").value = place.name
        updatePreviewCard("search-entity-headline", place.name)
        document.getElementById("id_google_maps_place_id").value = place.place_id
        if (place.rating) {
            document.getElementById("id_google_maps_rating").value = place.rating
        }
        document.getElementById("id_address").value = place.formatted_address
        const photo = place.photos[0].getUrl()
        document.getElementById("id_link_url").value = photo
        document.getElementById("search-entity-image").setAttribute("src", photo)

        // Make the image fields not required if we have one from google MAPS
        if (photo) {
            document.getElementById("id_uploaded_image").required = false;
            document.getElementById("id_alt_text").required = false;
            document.getElementById("id_permissions_confirmation").required = false;
        }
    });
}