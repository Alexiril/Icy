function makeStack(stackId, sides, maxSize = -1) {
    let stack = $(`#${stackId}`);
    if (stack.length != 0)
        stack.remove();
    stack = $(`<div class="side-stack ${sides}" id="${stackId}" data-maxsize="${maxSize}"></div>`);
    $("body").append(stack);
    return stack;
}

function addToStack(stackId, element, time_to_delete = -1) {
    let stack = $(`#${stackId}`);
    if (stack.length == 0)
        stack = makeStack(stackId, 'left-side bottom-side');
    const maxSize = parseInt(stack.attr('data-maxsize'), 10);
    if (maxSize != -1 && stack.children().length >= maxSize)
        stack.children(":first").remove();
    element.hide();
    stack.append(element);
    element.fadeIn(200);
    if (time_to_delete > 0)
        setTimeout(() => {
            element.fadeOut(200, () => element.remove())
        }, time_to_delete)
}

function clearStack(stackId) {
    let stack = $(`#${stackId}`);
    if (stack.length == 0)
        stack = makeStack(stackId, 'left-side bottom-side');
    stack.clear();
}