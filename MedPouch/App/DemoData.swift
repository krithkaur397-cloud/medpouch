//
//  DemoData.swift
//  MedPouch
//
//  Sample records for App Store screenshots. Compiled into Debug builds only, and used
//  only when the app is launched with -MedPouchDemo (the screenshots workflow does this).
//  The App Store build (Release) contains none of this.
//

#if DEBUG
import CoreData
import Foundation

enum DemoData {
    static var isRequested: Bool {
        ProcessInfo.processInfo.arguments.contains("-MedPouchDemo")
    }

    /// Tab to open at launch, from -MedPouchTab <n>
    static var requestedTab: Int? {
        let args = ProcessInfo.processInfo.arguments
        guard let index = args.firstIndex(of: "-MedPouchTab"), index + 1 < args.count else { return nil }
        return Int(args[index + 1])
    }

    static func installIfRequested(into context: NSManagedObjectContext) {
        guard isRequested else { return }

        let defaults = UserDefaults.standard
        defaults.set(true, forKey: "hasCompletedOnboarding")
        defaults.set(true, forKey: "hasDismissedFamilyHint")
        defaults.set("Alex Morgan", forKey: "fullName")
        defaults.set(date(1986, 4, 12).timeIntervalSince1970, forKey: "dateOfBirth")
        defaults.set("O+", forKey: "bloodType")
        defaults.set("Type 2 diabetes, mild asthma", forKey: "medicalConditions")
        defaults.set(true, forKey: "isOrganDonor")
        defaults.set(true, forKey: "showQRCode")

        let medicationRequest: NSFetchRequest<Medication> = Medication.fetchRequest()
        let existing = (try? context.count(for: medicationRequest)) ?? 0
        guard existing == 0 else { return }

        let now = Date()
        func ago(_ days: Double) -> Date { now.addingTimeInterval(-days * 86_400) }

        func medication(_ name: String, _ dosage: String, _ frequency: String, essential: Bool,
                        notes: String? = nil, member: UUID? = nil, added: Date) {
            let item = Medication(context: context)
            item.id = UUID()
            item.name = name
            item.dosage = dosage
            item.frequency = frequency
            item.isEssential = essential
            item.notes = notes
            item.familyMemberID = member
            item.dateAdded = added
        }
        medication("Metformin", "500 mg", "Twice daily", essential: true, notes: "Take with breakfast and dinner", added: ago(40))
        medication("Lisinopril", "10 mg", "Daily", essential: true, added: ago(30))
        medication("Albuterol inhaler", "2 puffs", "As needed", essential: true, notes: "Before exercise", added: ago(20))
        medication("Vitamin D3", "1000 IU", "Daily", essential: false, added: ago(10))

        func prescription(_ name: String, _ dosage: String, doctor: String, pharmacy: String,
                          refills: Int16, instructions: String, issued: Date) {
            let item = Prescription(context: context)
            item.id = UUID()
            item.medicationName = name
            item.dosage = dosage
            item.doctorName = doctor
            item.pharmacy = pharmacy
            item.refillsRemaining = refills
            item.instructions = instructions
            item.dateIssued = issued
            item.dateAdded = issued
        }
        prescription("Metformin", "500 mg", doctor: "Dr. Priya Patel", pharmacy: "Main Street Pharmacy",
                     refills: 3, instructions: "1 tablet twice daily with meals", issued: ago(40))
        prescription("Lisinopril", "10 mg", doctor: "Dr. Priya Patel", pharmacy: "Main Street Pharmacy",
                     refills: 5, instructions: "1 tablet every morning", issued: ago(30))
        prescription("Albuterol HFA", "90 mcg", doctor: "Dr. James Lee", pharmacy: "Riverside Pharmacy",
                     refills: 1, instructions: "2 puffs every 4 to 6 hours as needed", issued: ago(20))

        func allergy(_ allergen: String, _ severity: String, _ reaction: String, added: Date) {
            let item = Allergy(context: context)
            item.id = UUID()
            item.allergen = allergen
            item.severity = severity
            item.reaction = reaction
            item.dateAdded = added
        }
        allergy("Penicillin", "Severe", "Hives, swelling", added: ago(50))
        allergy("Peanuts", "Life-threatening", "Anaphylaxis, carries EpiPen", added: ago(45))

        func contact(_ name: String, _ relationship: String, _ phone: String, member: UUID? = nil, added: Date) {
            let item = Contact(context: context)
            item.id = UUID()
            item.name = name
            item.relationship = relationship
            item.phoneNumber = phone
            item.familyMemberID = member
            item.dateAdded = added
        }
        contact("Sam Morgan", "Spouse/Partner", "+1 555 201 4477", added: ago(50))
        contact("Dr. Priya Patel", "Doctor", "+1 555 310 2200", added: ago(40))

        let child = FamilyMember(context: context)
        child.id = UUID()
        child.name = "Mia Morgan"
        child.relationship = "Child"
        child.bloodType = "A+"
        child.dateOfBirth = date(2017, 9, 3)
        child.medicalConditions = "Eczema"
        child.dateAdded = ago(15)
        medication("Cetirizine", "5 mg", "Daily", essential: false, member: child.id, added: ago(15))
        contact("Sam Morgan", "Parent", "+1 555 201 4477", member: child.id, added: ago(15))

        try? context.save()
    }

    private static func date(_ year: Int, _ month: Int, _ day: Int) -> Date {
        Calendar(identifier: .gregorian).date(from: DateComponents(year: year, month: month, day: day)) ?? Date()
    }
}
#endif
