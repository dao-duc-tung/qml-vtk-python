import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.3
// import Renderer 1.0

// Rectangle {
ApplicationWindow {
    width: 500
    height: 600
    visible: true

    // FBORenderer{
    //     id: fboRenderItem
    //     anchors.fill: parent
    // }

    Text {
        text: "This is an openGl rendering with QQuickFrameBufferObject"
    }
}
