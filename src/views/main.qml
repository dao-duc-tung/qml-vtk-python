import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.3
import QtQuick.Controls.Material 2.2
import QmlVtk 1.0

ApplicationWindow {
    id: root
    objectName: 'MainView'
    minimumWidth: 1024
    minimumHeight: 700
    visible: true
    title: "Qml-Vtk-Python"

    Material.primary: Material.Indigo
    Material.accent: Material.LightBlue

    Rectangle {
        id: screenCanvasUI
        anchors.fill: parent

        Fbo {
            id: fbo
            objectName: "fbo"
            anchors.fill: parent

            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.AllButtons
                propagateComposedEvents: true

                onPressed: (mouse) => {
                    mouse.accepted = true;
                    this.parent.onMousePressed(
                        mouse.x, mouse.y, mouse.button,
                        mouse.buttons, mouse.modifiers);
                    MainCtrl.showPos(mouse.buttons, mouseX, mouseY);
                }

                onPositionChanged: (mouse) => {
                    this.parent.onMouseMove(mouse.x, mouse.y, mouse.button,
                                            mouse.buttons, mouse.modifiers);
                    MainCtrl.showPos(mouse.buttons, mouseX, mouseY);
                }

                onWheel: (wheel) => {
                    this.parent.onMouseWheel(wheel.angleDelta, wheel.buttons,
                                     wheel.inverted, wheel.modifiers,
                                     wheel.pixelDelta, wheel.x, wheel.y);

                    if (wheel.angleDelta.y < 0){
                        modelColorR.value -= 10;
                    }
                    else {
                        modelColorR.value += 10;
                    }
                }
            }
        }

        Button {
            id: demoBtn
            text: "Show/Hide Cylinder"
            highlighted: true
            anchors.right: openFileButton.left
            anchors.bottom: parent.bottom
            anchors.margins: 30
            onClicked: {
                MainCtrl.toggleCylinder();
            }
        }

        Button {
            id: openFileButton
            text: "Open File"
            highlighted: true
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 30
            onClicked: {
                fileDialog.visible = true;
            }
        }

        SpinBox {
            id: modelColorR
            value: 5
            from: 0
            to: 255
            stepSize: 5
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.leftMargin: 40
            anchors.topMargin: 40
            onValueChanged: setModelColor();
        }

        SpinBox {
            id: modelColorG
            value: 170
            from: 0
            to: 255
            stepSize: 5
            anchors.left: parent.left
            anchors.top: modelColorR.bottom
            anchors.leftMargin: 40
            anchors.topMargin: 40
            onValueChanged: setModelColor();
        }

        SpinBox {
            id: modelColorB
            value: 105
            from: 0
            to: 255
            stepSize: 5
            anchors.left: parent.left
            anchors.top: modelColorG.bottom
            anchors.leftMargin: 40
            anchors.topMargin: 40
            onValueChanged: setModelColor();
        }

        Label {
            id: posX
            text: "X: " + MainCtrl.posX
            font.pixelSize: 16
            anchors.bottom: posY.top
            anchors.left: parent.left
            anchors.margins: 40
        }

        Label {
            id: posY
            text: "Y: " + MainCtrl.posY
            font.pixelSize: 16
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.margins: 40
        }
    }

    FileDialog {
        id: fileDialog
        visible: false
        title: "Import model"
        folder: shortcuts.documents
        nameFilters: ["Mesh files" + "(*.stl *.STL *.obj *.OBJ)", "All files" + "(*)"]

        onAccepted: {
            MainCtrl.openModel(fileUrl);
        }
    }

    function setModelColor() {
        MainCtrl.setModelColor(modelColorR.value, modelColorG.value, modelColorB.value);
    }
}
