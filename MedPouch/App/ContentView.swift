//
//  ContentView.swift
//  MedicalWallet
//
//  Main tab bar
//

import SwiftUI

struct ContentView: View {
    @State private var selectedTab = ContentView.initialTab

    // Debug builds can open a given tab at launch (used for App Store screenshots)
    private static var initialTab: Int {
        #if DEBUG
        return DemoData.requestedTab ?? 0
        #else
        return 0
        #endif
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(0)

            MedicationsView()
                .tabItem {
                    Label("Medications", systemImage: "pills.fill")
                }
                .tag(1)

            NavigationView {
                PrescriptionsView()
            }
            .tabItem {
                Label("Prescriptions", systemImage: "doc.text.fill")
            }
            .tag(2)

            NavigationView {
                WalletCardView()
            }
            .tabItem {
                Label("Emergency", systemImage: "staroflife.fill")
            }
            .tag(3)

            NavigationView {
                ProfileView()
            }
            .tabItem {
                Label("Profile", systemImage: "person.crop.circle.fill")
            }
            .tag(4)
        }
    }
}

#Preview {
    ContentView()
        .environment(\.managedObjectContext, PersistenceController.preview.container.viewContext)
}
