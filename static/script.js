var timer;
var alert_popup_number;
var active_category = 0;

function translate(name) {
    name = name.replace(/§quote§/g, "'");
    name = name.replace(/§double_quotes§/g, '"');
    name = name.replace(/§and§/g, "&");
    return name;
}


window.onload = function() {
    function translateTextNode(node) {
        var translatedText = translate(node.textContent);
        node.textContent = translatedText;
    }

    function traverse(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            translateTextNode(node);
        } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'SCRIPT' && node.tagName !== 'STYLE') {
            node.childNodes.forEach(traverse);
        }
    }
    traverse(document.body);

};

function translateName() {
    let names = document.getElementsByClassName("translate-names")

    for (let i = 0; i < names.length; i++) {
        names[i].innerHTML = translate(names[i].innerHTML)
    }
}




function reloadItems(category) {
    active_category = category;
    const itemsList = document.getElementById("reload-items-list");
    fetch("/reloaditems", {
            method: "GET"
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            const tempElement = document.createElement('div');
            tempElement.innerHTML = html;
            itemsList.innerHTML = tempElement.innerHTML;
        })
        .catch(error => {
            console.error('Error:', error);
        });

}

function reloadCounters() {
    const countersContainer = document.getElementById("counters");
    const countersElements = countersContainer.querySelectorAll('.counter-class');

    fetch("/reloaditems", {
            method: "GET"
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(html => {
            const tempElement = document.createElement('div');
            tempElement.innerHTML = html;

            countersElements.forEach((counterElement, index) => {
                counterElement.innerHTML = tempElement.querySelectorAll('.counter-class')[index].innerHTML;
            });

        })
        .catch(error => {
            console.error('Error:', error);
        });
}




function activate_popup(div) {
    let popup = document.getElementById(div);
    let popups = document.getElementsByClassName("popup")
    let values = document.getElementsByClassName("create-value");
    let select = document.getElementById("select-value");
    let wall = document.getElementById("wall");
    wall.onclick = function() {
        activate_popup(div);
    }
    if (popup.style.opacity === "1") {
        clearTimeout();
        popup.style.opacity = "0";
        popup.style.animation = "slide-down 0.3s ease 0s 1 normal none";
        timer = setTimeout(function() {
            popup.style.display = 'none';
        }, 300);
        wall.classList.remove("wall");
        for (let i = 0; i < values.length; i++) {
            values[i].value = "";
        }
    } else {
        clearTimeout(timer);
        for (let i = 0; i < popups.length; i++) {
            popups[i].style.display = "none";
        }
        if (select) {
            select.value = "1";
        }
        popup.style.animation = "slide-up 0.3s ease 0s 1 normal none";
        popup.style.opacity = "1";
        popup.style.display = 'block';
        wall.classList.add("wall");
    }
};

function activate_edit(div, list_code, list_name, current_users) {
    div = translate(div);
    list_code = translate(list_code);
    list_name = translate(list_name);
    current_users = translate(current_users);
    let p = document.getElementById("edit-p");
    let list = document.getElementById("list");
    let users = document.getElementById("users-edit");
    let popup = document.getElementById(div);
    let popups = document.getElementsByClassName("popup")
    let values = document.getElementsByClassName("create-value");
    let wall = document.getElementById("wall");
    let new_name = document.getElementById("new-name");
    new_name.value = list_name;
    list.value = list_code;
    users.min = current_users;
    users.value = current_users;
    p.innerHTML = "Edit " + '"' + list_name + '"';
    wall.onclick = function() {
        activate_edit(div, list_code, list_name, current_users);
    }
    if (popup.style.opacity === "1") {
        clearTimeout();
        popup.style.opacity = "0";
        popup.style.animation = "slide-down 0.3s ease 0s 1 normal none";
        timer = setTimeout(function() {
            popup.style.display = 'none';
        }, 300);
        wall.classList.remove("wall");
        for (let i = 0; i < values.length; i++) {
            values[i].value = "";
        }
    } else {
        clearTimeout(timer);
        for (let i = 0; i < popups.length; i++) {
            popups[i].style.display = "none";
        }
        popup.style.animation = "slide-up 0.3s ease 0s 1 normal none";
        popup.style.opacity = "1";
        popup.style.display = 'block';
        wall.classList.add("wall");
    }

};

function activate_product_edit(div, name, brand, image, priority, product_id) {
    div = translate(div);
    name = translate(name);
    brand = translate(brand);
    image = translate(image);
    let new_brand = document.getElementById("brand-name");
    let new_image = document.getElementById("image-link");
    let popup = document.getElementById(div);
    let popups = document.getElementsByClassName("popup")
    let values = document.getElementsByClassName("create-value");
    let wall = document.getElementById("wall");
    let new_name = document.getElementById("product-name");
    let select = document.getElementById("select-new-value");
    let product = document.getElementById("product")
    product.value = product_id;
    new_name.value = name;
    new_brand.value = brand;
    if (image === "/static/image.svg") {
        new_image.value = "";
    } else {
        new_image.value = image;
    }
    select.value = priority;
    wall.onclick = function() {
        activate_product_edit(div, name, brand, image);
    }
    if (popup.style.opacity === "1") {
        clearTimeout();
        popup.style.opacity = "0";
        popup.style.animation = "slide-down 0.3s ease 0s 1 normal none";
        timer = setTimeout(function() {
            popup.style.display = 'none';
        }, 300);
        wall.classList.remove("wall");
        for (let i = 0; i < values.length; i++) {
            values[i].value = "";
        }
    } else {
        clearTimeout(timer);
        for (let i = 0; i < popups.length; i++) {
            popups[i].style.display = "none";
        }
        popup.style.animation = "slide-up 0.3s ease 0s 1 normal none";
        popup.style.opacity = "1";
        popup.style.display = 'block';
        wall.classList.add("wall");
    }

};

function activate_favorite(div, name, brand, image, product_id) {
    div = translate(div);
    name = translate(name);
    brand = translate(brand);
    image = translate(image);
    let new_brand = document.getElementById("favorite-brand");
    let new_image = document.getElementById("favorite-image-link");
    let popup = document.getElementById(div);
    let popups = document.getElementsByClassName("popup")
    let values = document.getElementsByClassName("create-value");
    let wall = document.getElementById("wall");
    let new_name = document.getElementById("favorite-name");
    let product = document.getElementById("favorite")
    product.value = product_id;
    new_name.value = name;
    new_brand.value = brand;
    if (image === "/static/image.svg") {
        new_image.value = "";
    } else {
        new_image.value = image;
    }
    wall.onclick = function() {
        activate_favorite(div, name, brand, image);
    }
    if (popup.style.opacity === "1") {
        clearTimeout();
        popup.style.opacity = "0";
        popup.style.animation = "slide-down 0.3s ease 0s 1 normal none";
        timer = setTimeout(function() {
            popup.style.display = 'none';
        }, 300);
        wall.classList.remove("wall");
        for (let i = 0; i < values.length; i++) {
            values[i].value = "";
        }
    } else {
        clearTimeout(timer);
        for (let i = 0; i < popups.length; i++) {
            popups[i].style.display = "none";
        }
        popup.style.animation = "slide-up 0.3s ease 0s 1 normal none";
        popup.style.opacity = "1";
        popup.style.display = 'block';
        wall.classList.add("wall");
    }

};

function activate_delete(div, list_code, list_name, product_id, action_type) {
    div = translate(div);
    list_code = translate(list_code);
    list_name = translate(list_name);
    if (list_code) {
        let p = document.getElementById("delete-p");
        let list = document.getElementById("list-delete");
        let list_quit = document.getElementById("list-quit");
        let span = document.getElementById("delete-span");
        let title = document.getElementById("quit-p");
        list.value = list_code;
        list_quit.value = list_code;
        title.innerHTML = "Quit " + '"' + list_name + '"';
        p.innerHTML = "Delete " + '"' + list_name + '"';
    }
    if (product_id) {
        let action = document.getElementById("delete-action");
        let id = document.getElementById("product-delete");
        id.value = product_id;
        if (action_type == "favorite") {
            action.value = "favorite";
        }
        if (action_type == "history") {
            action.value = "history";
        }
    }
    let popup = document.getElementById(div);
    let popups = document.getElementsByClassName("popup")
    let wall = document.getElementById("wall");
    wall.onclick = function() {
        activate_delete(div, list_code, list_name, '');
    }
    if (popup.style.opacity === "1") {
        clearTimeout();
        popup.style.opacity = "0";
        popup.style.animation = "slide-down 0.3s ease 0s 1 normal none";
        timer = setTimeout(function() {
            popup.style.display = 'none';
        }, 300);
        wall.classList.remove("wall");
    } else {
        clearTimeout(timer);
        for (let i = 0; i < popups.length; i++) {
            popups[i].style.display = "none";
        }
        popup.style.animation = "slide-up 0.3s ease 0s 1 normal none";
        popup.style.opacity = "1";
        popup.style.display = 'block';
        wall.classList.add("wall");
    }

}

function zoom_image(div, image) {
    let popup = document.getElementById(div);
    let values = document.getElementsByClassName("create-value");
    let wall = document.getElementById("wall");
    if (image.includes("openfoodfacts.org")) {
        image = image.replace(/.200.jpg/g, ".400.jpg");
    }
    wall.onclick = function() {
        zoom_image(div, image);
    }

    if (popup.style.display === "block") {
        popup.style.display = 'none';
        wall.classList.remove("wall");
    } else {
        popup.src = image;
        popup.style.display = 'block';
        wall.classList.add("wall");
    }
};

function addFromResults(name, brand, image, div, button) {
    name = translate(name);
    brand = translate(brand);
    if (button) {
        var item = document.getElementById(div);
        var onclick = button.onclick;
        button.onclick = "";
    }
    $.ajax({
        type: "POST",
        url: "/add",
        data: {
            "name": name,
            "brand": brand,
            "image": image,
            "action": 'product',
        },
        success: function(response) {
            if (div) {
                item.style.display = "none";
                reloadCounters()
            }
        },
        error: function(xhr, status, error) {
            if (button) {
                button.onclick = onclick;
            }
            alert("Unable to update the product status. Please retry.")
            console.error(error);
        }
    })
}

function editFavorite(name, brand, image, div, button) {
    name = translate(name);
    brand = translate(brand);
    if (button) {
        var item = document.getElementById(div);
        var onclick = button.onclick;
        button.onclick = "";
    }
    $.ajax({
        type: "POST",
        url: "/favorite",
        data: {
            "name": name,
            "brand": brand,
            "image": image,
        },
        success: function(response) {
            if (div) {
                item.style.display = "none";
                reloadCounters()
            }
        },
        error: function(xhr, status, error) {
            if (button) {
                button.onclick = onclick;
            }
            alert("Unable to update the product status. Please retry.")
            console.error(error);
        }
    })
}


function complete(div, product_id, button) {
    let item = document.getElementById(div);
    let onclick = button.onclick;
    button.onclick = "";
    $.ajax({
        type: "POST",
        url: "/complete",
        data: {
            "product": product_id,
        },
        success: function(response) {
            item.style.display = "none";
            reloadCounters()
        },
        error: function(xhr, status, error) {
            button.onclick = onclick;
            console.error(error);
            alert("Unable to update the product status. Please retry.")
        }
    });
}

function removeUser(button, div, user_id) {
    let item = document.getElementById(div);
    let onclick = button.onclick;
    button.onclick = "";
    $.ajax({
        type: "POST",
        url: "/kick",
        data: {
            "user": user_id,
        },
        success: function(response) {
            item.style.display = "none";
        },
        error: function(xhr, status, error) {
            button.onclick = onclick;
            console.error(error);
            alert("Unable to kick the user. Please retry.")
        }
    });
}


function editProduct(button, name_input, brand_input, image_input, priority_input, id_input, favorite_action) {
    let name = document.getElementById(name_input);
    let brand = document.getElementById(brand_input);
    let image = document.getElementById(image_input);
    let priority = document.getElementById(priority_input);
    let id = document.getElementById(id_input);
    let action = document.getElementById(favorite_action);
    let onclick = button.onclick;
    button.onclick = "";
    $.ajax({
        type: "POST",
        url: "/edit",
        data: {
            "name": name.value,
            "brand": brand.value,
            "image": image.value,
            "priority": priority.value,
            "action": action.value,
            "product": id.value,
        },
        success: function(response) {
            button.onclick = onclick;
            activate_favorite('edit-popup', '', '', '');
            reloadItems(0);
        },
        error: function(xhr, status, error) {
            button.onclick = onclick;
            console.error(error);
            alert("Unable to edit the product. Please retry.")
        }
    });
}

function addProduct(button, name_input, brand_input, image_input, priority_input, favorite_action) {
    let name = document.getElementById(name_input);
    let brand = document.getElementById(brand_input);
    let image = document.getElementById(image_input);
    let priority = document.getElementById(priority_input);
    let action = document.getElementById(favorite_action);
    let onclick = button.onclick;
    button.onclick = "";
    $.ajax({
        type: "POST",
        url: "/add",
        data: {
            "name": name.value,
            "brand": brand.value,
            "image": image.value,
            "priority": priority.value,
            "action": action.value,
        },
        success: function(response) {
            button.onclick = onclick;
            activate_popup('create-popup');
            reloadItems(0);
        },
        error: function(xhr, status, error) {
            button.onclick = onclick;
            console.error(error);
            alert("Unable to add the product. Please retry.")
        }
    });
}

function deleteProduct(button) {
    let action = document.getElementById('delete-action');
    let product = document.getElementById('product-delete');
    let onclick = button.onclick;
    button.onclick = "";
    $.ajax({
        type: "POST",
        url: "/delete",
        data: {
            "product": product.value,
            "action": action.value,
        },
        success: function(response) {
            button.onclick = onclick;
            activate_delete('delete-popup', '', '', '', '');
            if (action.value === "history") {
                reloadItems(1);
            }
            if (action.value === "favorite") {
                reloadItems(2);
            }
        },
        error: function(xhr, status, error) {
            button.onclick = onclick;
            console.error(error);
            alert("Unable to remove the product. Please retry.")
        }
    });
}


function addProduct(button, name_input, brand_input, image_input, priority_input, favorite_action) {
    let name = document.getElementById(name_input);
    let brand = document.getElementById(brand_input);
    let image = document.getElementById(image_input);
    let priority = document.getElementById(priority_input);
    let action = document.getElementById(favorite_action);
    let onclick = button.onclick;
    button.onclick = "";
    $.ajax({
        type: "POST",
        url: "/add",
        data: {
            "name": name.value,
            "brand": brand.value,
            "image": image.value,
            "priority": priority.value,
            "action": action.value,
        },
        success: function(response) {
            button.onclick = onclick;
            activate_popup('create-popup');
            reloadItems(0);
        },
        error: function(xhr, status, error) {
            button.onclick = onclick;
            console.error(error);
            alert("Unable to add the product. Please retry.")
        }
    });
}

function addFavorite(button, name_input, brand_input, image_input, favorite_action) {
    let name = document.getElementById(name_input);
    let brand = document.getElementById(brand_input);
    let image = document.getElementById(image_input);
    let action = document.getElementById(favorite_action);
    let onclick = button.onclick;
    button.onclick = "";
    $.ajax({
        type: "POST",
        url: "/add",
        data: {
            "name": name.value,
            "brand": brand.value,
            "image": image.value,
            "action": action.value,
        },
        success: function(response) {
            button.onclick = onclick;
            activate_popup('create-favorite-popup');
            reloadItems(2);
        },
        error: function(xhr, status, error) {
            button.onclick = onclick;
            console.error(error);
            alert("Unable to add the product. Please retry.")
        }
    });
}




function editFromFavorites(button, name_input, brand_input, image_input, id_input, favorite_action) {
    let name = document.getElementById(name_input);
    let brand = document.getElementById(brand_input);
    let image = document.getElementById(image_input);
    let id = document.getElementById(id_input);
    let action = document.getElementById(favorite_action);
    let onclick = button.onclick;
    button.onclick = "";
    $.ajax({
        type: "POST",
        url: "/edit",
        data: {
            "name": name.value,
            "brand": brand.value,
            "image": image.value,
            "action": action.value,
            "product": id.value,
        },
        success: function(response) {
            button.onclick = onclick;
            activate_favorite('favorite-edit-popup', '', '', '');
            reloadItems(2);
        },
        error: function(xhr, status, error) {
            button.onclick = onclick;
            console.error(error);
            alert("Unable to edit the product. Please retry.")
        }
    });
}

function display_edit_buttons() {
    let edit_buttons = document.getElementsByClassName("list-edit-icon");
    let add_buttons = document.getElementsByClassName("add-edit-icon");
    let x = document.getElementById("x");
    let edit = document.getElementById("edic");
    let edit_circle = document.getElementsByClassName("circle-edit-button");
    let counter = document.getElementById("items-counter")

    let number = "";
    let counterText = counter.textContent;
    for (let i = 0; i < counterText.length; i++) {
        if (!isNaN(parseInt(counterText[i]))) {
            number += counterText[i];
        }
    }
    if (number == "0") {
        return;
    }

    if (edit_buttons[0].style.display === "none" || edit_buttons[0].style.display === "") {
        for (let i = 0; i < add_buttons.length; i++) {
            add_buttons[i].style.display = "none";
            edit_buttons[i].style.display = "block";
            x.style.display = "block";
            edit.style.display = "none";
            edit_circle[0].style.backgroundColor = "#D65D20";
        }
    } else if (add_buttons[0].style.display === "none" || add_buttons[0].style.display === "") {
        for (let i = 0; i < add_buttons.length; i++) {
            add_buttons[i].style.display = "block";
            edit_buttons[i].style.display = "none";
            x.style.display = "none";
            edit.style.display = "block";
            edit_circle[0].style.backgroundColor = "#D5A021";
        }
    }
};

function activate_category() {
    let items = document.getElementById("items-category");
    let history = document.getElementById("history-category");
    let favorites = document.getElementById("favorites-category");
    let divs = document.getElementsByClassName("bottom-bar-item");
    let cat1 = document.getElementById("cat1");
    let cat2 = document.getElementById("cat2");
    let cat3 = document.getElementById("cat3")

    if (active_category == 0) {
        for (let i = 0; i < divs.length; i++) {
            divs[i].classList.remove("bottom-bar-item-active");
        }
        cat3.onclick = function() {
            reloadItems(2);
        };
        cat2.onclick = function() {
            reloadItems(1);
        };
        cat1.onclick = null;
        cat1.classList.add("bottom-bar-item-active");
        history.style.display = "none";
        items.style.display = "block";
        favorites.style.display = "none";
    }

    if (active_category == 1) {
        for (let i = 0; i < divs.length; i++) {
            divs[i].classList.remove("bottom-bar-item-active");
        }
        cat3.onclick = function() {
            reloadItems(2);
        };
        cat1.onclick = function() {
            reloadItems(0);
        };
        cat2.onclick = null;
        cat2.classList.add("bottom-bar-item-active");
        history.style.display = "block";
        items.style.display = "none";
        favorites.style.display = "none";
    }

    if (active_category == 2) {
        for (let i = 0; i < divs.length; i++) {
            divs[i].classList.remove("bottom-bar-item-active");
        }
        cat2.onclick = function() {
            reloadItems(1);
        };
        cat1.onclick = function() {
            reloadItems(0);
        };
        cat3.onclick = null;
        cat3.classList.add("bottom-bar-item-active");
        history.style.display = "none";
        items.style.display = "none";
        favorites.style.display = "block";
    }
}

function activateSearch() {
    let bar = document.getElementById("mobile-search");
    let wall = document.getElementById("wall");
    let input = document.getElementById("search-input");
    let logo = document.getElementById("logo");

    wall.onclick = function() {
        activateSearch();
    }
    if (bar.style.display === "flex") {
        clearTimeout();
        logo.style.display = "block";
        bar.style.display = "none";
        wall.classList.remove("wall");
    } else {
        clearTimeout(timer);
        logo.style.display = "none";
        bar.style.display = "flex";
        input.focus();
        wall.classList.add("wall");
    }

}
