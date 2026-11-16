import Foundation
import CoreBluetooth

let outPath = (ProcessInfo.processInfo.environment["HOME"] ?? "/tmp") + "/Documents/Coding/RoomClimate/ble.jsonl"
FileManager.default.createFile(atPath: outPath, contents: nil) 
let fh = FileHandle(forWritingAtPath: outPath)!
fh.seekToEndOfFile()
func hex(_ d: Data) -> String { d.map { String(format: "%02x", $0) }.joined() }

class D: NSObject, CBCentralManagerDelegate {
    var m: CBCentralManager!
    override init() { super.init(); m = CBCentralManager(delegate: self, queue: nil) }
    func centralManagerDidUpdateState(_ c: CBCentralManager) {
        let s = "{\"state\":\(c.state.rawValue),\"ts\":\(Date().timeIntervalSince1970)}\n"
        fh.write(s.data(using: .utf8)!)
        if c.state == .poweredOn { c.scanForPeripherals(withServices: nil, options: [CBCentralManagerScanOptionAllowDuplicatesKey: true]) }
    }
    func centralManager(_ c: CBCentralManager, didDiscover p: CBPeripheral, advertisementData a: [String: Any], rssi: NSNumber) {
        let mfr = a[CBAdvertisementDataManufacturerDataKey] as? Data
        let sd = a[CBAdvertisementDataServiceDataKey] as? [CBUUID: Data] ?? [:]
        let isSB = (mfr.map { $0.count >= 2 && $0[0] == 0x69 && $0[1] == 0x09 } ?? false) || sd.keys.contains(CBUUID(string: "FD3D"))
        if !isSB { return }
        var sds: [String: String] = [:]
        for (k, v) in sd { sds[k.uuidString] = hex(v) }
        let o: [String: Any] = ["ts": Date().timeIntervalSince1970, "id": p.identifier.uuidString, "name": p.name ?? "", "rssi": rssi, "mfr": mfr.map(hex) ?? "", "sd": sds]
        if let j = try? JSONSerialization.data(withJSONObject: o) { fh.write(j); fh.write("\n".data(using: .utf8)!) }
    }
}
let d = D()
RunLoop.main.run()
