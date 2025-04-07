using UnityEditor;
using UnityEditor.SceneManagement;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChangeSceneTab : Editor
{
    #region OmniShift

    [MenuItem("Scenes/UserStudy/Menu")]
    public static void LoadMenu()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/UserStudy/Menu.unity");
        }
        
    }

    [MenuItem("Scenes/UserStudy/Drawing")]
    public static void LoadDrawing()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/UserStudy/Drawing.unity");
        }

    }

    [MenuItem("Scenes/UserStudy/Animal")]
    public static void LoadAnimal()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/UserStudy/Animal.unity");
        }

    }

    [MenuItem("Scenes/UserStudy/AnimalFace")]
    public static void LoadAnimalFace()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/UserStudy/AnimalFace.unity");
        }

    }

    //[MenuItem("Scenes/UserStudy/SpaceShooter")]
    //public static void LoadSpaceShooter()
    //{
    //    if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
    //    {
    //        EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/UserStudy/SpaceShooter.unity");
    //    }

    //}

    [MenuItem("Scenes/UserStudy/SpaceWithDrawing")]
    public static void LoadSpaceShooterDrawing()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/UserStudy/SpaceWithDrawing.unity");
        }

    }

    [MenuItem("Scenes/UserStudy/Kanji")]
    public static void LoadKanji()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/UserStudy/Kanji.unity");
        }

    }

    [MenuItem("Scenes/UserStudy/Desk")]
    public static void LoadDesk()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/UserStudy/CustomizableDesk.unity");
        }

    }

    [MenuItem("Scenes/UserStudy/Globe")]
    public static void LoadGlobe()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/UserStudy/Globe.unity");
        }

    }

    #endregion


    #region WebbedHand

    [MenuItem("HandScenes/WebbedHand")]
    public static void LoadHand()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/OmniShiftResources/Scenes/OmniCamera/OmniHands/OmniWebbedHands.unity");
        }

    }
    

    #endregion

    #region Pneumatic based

    [MenuItem("PneumaticScenes/StarConstellations")]
    public static void LoadStars()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/PneumaticShift/Scenes/StarConstellations.unity");
        }

    }

    [MenuItem("PneumaticScenes/ExtendArea")]
    public static void LoadArea()
    {
        if (EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
        {
            EditorSceneManager.OpenScene("Assets/PneumaticShift/Scenes/ExtendArea.unity");
        }

    }

    #endregion
}
