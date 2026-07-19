plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.dragverse.capture"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.dragverse.capture"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"

        // Point the app at the orchestrator without rebuilding config into source:
        //   ./gradlew installDebug -PorchestratorUrl=http://10.0.2.2:8000
        buildConfigField(
            "String",
            "ORCHESTRATOR_URL",
            "\"${project.findProperty("orchestratorUrl") ?: "http://10.0.2.2:8000"}\"",
        )
    }

    buildFeatures {
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("com.google.ar:core:1.44.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
}
