function generateRangeSelector(
    targetElementId,
    targetLowerInputId,
    targetUpperInputId,
    targetDisplayLowerId,
    targetDisplayUpperId,
    min,
    max,
    startLower,
    startUpper
) {
    // Generate a single range selector slider to feed an upper and lower input element.
    const rangeSelector = document.querySelector('#' + targetElementId);
    const inputLower = document.querySelector("#" + targetLowerInputId)
    const inputUpper = document.querySelector("#" + targetUpperInputId)
    const displayLower = document.querySelector("#" + targetDisplayLowerId)
    const displayUpper = document.querySelector("#" + targetDisplayUpperId)
    let [lower, upper] = [startLower, startUpper]
    displayLower.innerHTML = lower
    displayUpper.innerHTML = upper

    new mdb.MultiRangeSlider(rangeSelector, {
        startValues: [lower, upper],
        min: min,
        max: max,
    });

    rangeSelector.addEventListener('value.mdb.multiRangeSlider', (e) => {
        [lower, upper] = e.values.rounded
        if (lower < min) {
            lower = 0
        }
        if (upper > max) {
            upper = max
        }
        if (upper < lower) {
            upper = lower
        }
        if (lower > upper) {
            lower = upper
        }

        displayLower.innerHTML = lower
        displayUpper.innerHTML = upper
        inputLower.value = lower
        inputUpper.value = upper
    });
}

function clearChildren(element) {
    for (var i = 0; i < element.childNodes.length; i++) {
        var e = element.childNodes[i];
        if (e.tagName) switch (e.tagName.toLowerCase()) {
            case 'input':
                switch (e.type) {
                    case "radio":
                    case "checkbox":
                        e.checked = false;
                        break;
                    case "button":
                    case "submit":
                    case "image":
                        break;
                    default:
                        e.value = '';
                        break;
                }
                break;
            case 'select':
                e.selectedIndex = 0;
                break;
            case 'textarea':
                e.innerHTML = '';
                break;
            default:
                clearChildren(e);
        }
    }
}

function replaceallDescendantIds(node, fromRegex, toString) {
    // Replace the ID of all child nodes, using a regex.
    for (var i = 0; i < node.children.length; i++) {
        var gchild = node.children[i];
        console.log(gchild.id)
        gchild.id = gchild.id.replace(fromRegex, toString)
        console.log(gchild.id)
        replaceallDescendantIds(gchild);
    }
}

//TODO - Yo, before you went to bed you were trying to get all the child forms
// to renumber by recursively changing the child IDs using a regexp.

function dynamicFormsetInit(formContainerId, addButtonId, endMarkerId) {
    // Add a new row to a dynamic formset.
    const formTable = document.getElementById(formContainerId)
    const addButton = document.getElementById(addButtonId)
    const endmarker = document.getElementById(endMarkerId)

    function addForm(e) {
        e.preventDefault()
        const newForm = formTable.children[formTable.children.length - 1].cloneNode(true)
        const addedForm = formTable.insertBefore(newForm, endmarker)

        // Go through and renumber all the forms
        const formRegex = RegExp(`form-[0-9]-`, 'g')
        for (let i = 0; i < formTable.children.length; i++) {
            const child = formTable.children[i]
            replaceallDescendantIds(child, formRegex, `form-${i}-`)
        }

        clearChildren(addedForm)
    }

    addButton.addEventListener("click", addForm)
}

function dynamicFormsetRemoveRow(element) {
    // Remove a row from a dynamic formset.
    if (element.parentElement.parentElement.parentElement.children.length > 1) {
        element.parentElement.parentElement.remove()
    }
}