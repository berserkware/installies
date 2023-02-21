function deleteScript(scriptId) {
  document.getElementById(scriptId).remove()
}

function createScriptDiv(scriptId) {
  // creates the script div to put all the inputs in
  var scriptDiv = document.createElement('div');
  
  scriptDiv.id = 'script-' + scriptId;
  scriptDiv.className = 'script shadow-box colour-yellow';
  
  return scriptDiv;
}

function createScriptHeading() {
  // creates the heading
  var scriptHeading = document.createElement('h2');
  scriptHeading.className = 'script-heading';
  scriptHeading.innerHTML = 'Script';
  
  return scriptHeading;
}

function createScriptActionLabel(scriptId) {
  // creates the script action drop down label
  var scriptActionDropDownLabel = document.createElement('label');
  scriptActionDropDownLabel.setAttribute('for', 'script-'+scriptId+'-action');
  scriptActionDropDownLabel.innerHTML = 'Script Action:';
  
  return scriptActionDropDownLabel;
}

function createScriptActionDropdown(scriptId) {
  // creates the script action drop down
  scriptActionDropDown = document.createElement('select')
  scriptActionDropDown.setAttribute('name', 'script-'+scriptId+'-action')
  scriptActionDropDown.id = 'script-'+scriptId+'-action'
  
  // adds all the entries to the drop down
  var possibleActions = ['install', 'remove']
  for (let i = 0; i < possibleActions.length; i++) {
    var possibleAction = document.createElement('option')
    possibleAction.value = possibleActions[i]
    possibleAction.innerText = possibleActions[i]
    scriptActionDropDown.appendChild(possibleAction)
  }
  
  return scriptActionDropDown
}

function createScriptVarientContainer(scriptId) {
  // creates the script varient container
  scriptVarientContainer = document.createElement('div')
  scriptVarientContainer.id = 'script-'+scriptId+'-varient-container'
  
  return scriptVarientContainer
}

function createAddVarientButton(scriptId) {
  // creates the add varient button
  addVarientButton = document.createElement('button')
  addVarientButton.type = 'button'
  addVarientButton.setAttribute('onclick', 'addScriptVarient("' + 'script-'+scriptId+ '-varient-container' + '", '+scriptId+')');
  addVarientButton.innerText = 'Add Varient'
  
  return addVarientButton
}

function createScriptDeleteButton(scriptId) {
  // creates the remove script button
  var removeScriptButton = document.createElement('button')
  removeScriptButton.type = 'button'
  removeScriptButton.setAttribute('onclick', 'deleteScript("script-' + scriptId + '")')
  removeScriptButton.innerText = 'Remove Script'
  
  return removeScriptButton
}

function addScript(container) {
  // gets the container to put the scripts in
  scriptContainer = document.getElementById(container);
  
  // creates an random id for the script's id
  scriptId = Math.floor(Math.random() * (999999 - 100000) + 100000);
  
  var scriptDiv = createScriptDiv(scriptId)
  
  // adds the heading to the script
  var scriptHeading = createScriptHeading()
  scriptDiv.appendChild(scriptHeading)
  
  // creates the script action drop down label
  var scriptActionDropDownLabel = createScriptActionLabel(scriptId)
  scriptDiv.appendChild(scriptActionDropDownLabel)
  
  // creates the script action drop down
  var scriptActionDropDown = createScriptActionDropdown(scriptId)
  scriptDiv.appendChild(scriptActionDropDown)
  
  // creates the script varient container
  var scriptVarientContainer = createScriptVarientContainer(scriptId)
  scriptDiv.appendChild(scriptVarientContainer)
  
  var addVarientButton = createAddVarientButton(scriptId)
  scriptDiv.appendChild(addVarientButton)
  
  // adds a break line
  breakLine = document.createElement('br')
  scriptDiv.appendChild(breakLine)
  
  // creates the script delete button
  var scriptDeleteButton = createScriptDeleteButton(scriptId)
  scriptDiv.appendChild(scriptDeleteButton)
  
  // adds the script div to the container
  scriptContainer.appendChild(scriptDiv)
}

function createScriptVarientDiv(scriptId, varientId) {
  // creates the script varient div
  var scriptVarientDiv = document.createElement('div')
  scriptVarientDiv.className = 'script-varient shadow-box colour-purple'
  scriptVarientDiv.id = 'script-' + scriptId + '-varient-' + varientId
  
  return scriptVarientDiv
}

function createScriptVarientHeader() {
  // creates the script varient header
  var scriptVarientHeader = document.createElement('h2')
  scriptVarientHeader.className = 'varient-heading'
  scriptVarientHeader.innerText = 'Script Varient'

  return scriptVarientHeader
}

function createScriptVarientTextarea(scriptId, varientId) {
  // creates the textarea for the script
  var scriptVarientTextarea = document.createElement('textarea')
  scriptVarientTextarea.name = 'script-' + scriptId + '-varient-' + varientId + '-textarea';
  scriptVarientTextarea.cols = '75';
  scriptVarientTextarea.rows = '25';
  scriptVarientTextarea.className = 'script-textarea';
  scriptVarientTextarea.spellcheck = 'false'
  scriptVarientTextarea.innerText = ''
  
  return scriptVarientTextarea
}

function createScriptVarientCompatibleDistrosContainer() {
  compatibleDistrosContainer = document.createElement('div');
  compatibleDistrosContainer.className = 'compatable-distros-container';
  
  return compatibleDistrosContainer;
}

function createScriptVarientCompatibleDistrosContainerHeader() {
  compatibleDistrosContainerHeader = document.createElement('h3');
  compatibleDistrosContainerHeader.innerText = 'Compatible Linux Distributions:';
  
  return compatibleDistrosContainerHeader;
}

function createScriptVarientCompatibleDistrosUl(varientId, scriptId) {
  compatibleDistrosUl = document.createElement('ul');
  compatibleDistrosUl.className = 'compatible-distro-list';
  
  // adds the distro options
  var distroOptions = [
    'Ubuntu',
    'Arch',
    'Manjaro',
    'Debian',
    'Gentoo',
    'Mint',
    'Fedora',
    'Opensuse',
  ];

  for (var i = 0; i < distroOptions.length; i++) {
    // creates the list item
    listItem = document.createElement('li');

    // creates the text node
    textNode = document.createTextNode(distroOptions[i]);

    // creates the checkbox input
    checkboxInput = document.createElement('input');
    checkboxInput.type = 'checkbox';
    checkboxInput.name = 'script-' + scriptId + '-varient-' + varientId + '-compatible-' + distroOptions[i].toLowerCase();
    
    // combines them all
    listItem.appendChild(textNode);
    listItem.appendChild(checkboxInput);

    // adds it to the compatible distros ul

    compatibleDistrosUl.appendChild(listItem);
  }
  
  return compatibleDistrosUl;
}

function createDeleteScriptVarientButton(scriptId, varientId) {
  // creates the add varient button
  deleteVarientButton = document.createElement('button');
  deleteVarientButton.type = 'button';
  deleteVarientButton.setAttribute('onclick', 'deleteScriptVarient("' + 'script-' + scriptId + '-varient-' + varientId+'")');
  deleteVarientButton.innerText = 'Remove Varient';
  
  return deleteVarientButton;
}

function addScriptVarient(containerId, scriptId) {
  scriptVarientContainer = document.getElementById(containerId)

  // creates an random id for the varient's id
  var varientId = Math.floor(Math.random() * (999999 - 100000) + 100000);

  // creates the script varient div
  var scriptVarientDiv = createScriptVarientDiv(scriptId, varientId)

  // creates the script varient header
  var scriptVarientHeader = createScriptVarientHeader()
  scriptVarientDiv.appendChild(scriptVarientHeader)

  scriptVarientTextarea = createScriptVarientTextarea(scriptId, varientId)
  scriptVarientDiv.appendChild(scriptVarientTextarea)
  
  // creates the container for the compatible distro checkboxs
  compatibleDistrosContainer = createScriptVarientCompatibleDistrosContainer()
  
  // creates the header for the container
  compatibleDistrosContainerHeader = createScriptVarientCompatibleDistrosContainerHeader()
  compatibleDistrosContainer.appendChild(compatibleDistrosContainerHeader);
  
  // creates the ul with the distros
  compatibleDistrosUl = createScriptVarientCompatibleDistrosUl(varientId, scriptId)

  // adds the ul to the compatable distros container
  compatibleDistrosContainer.appendChild(compatibleDistrosUl)
  
  scriptVarientDiv.appendChild(compatibleDistrosContainer)
  
  // creates the delete button
  varientDeleteButton = createDeleteScriptVarientButton(scriptId, varientId)
  scriptVarientDiv.appendChild(varientDeleteButton)

  scriptVarientContainer.appendChild(scriptVarientDiv)
}

function deleteScriptVarient(container) {
  document.getElementById(container).remove()
}