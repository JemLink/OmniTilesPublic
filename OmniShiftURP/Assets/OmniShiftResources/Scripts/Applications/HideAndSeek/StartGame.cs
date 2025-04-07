using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.SceneManagement;

[System.Serializable]
public class StartGameEvent : UnityEvent { }

public class StartGame : MonoBehaviour
{
    public StartGameEvent onStartingGame;

    public GameObject[] objectsToActivate;
    public GameObject[] objectsToDeactivate;

    public 

    // Start is called before the first frame update
    void Start()
    {
        for (int i = 0; i < objectsToActivate.Length; i++)
        {
            objectsToActivate[i].SetActive(false);
        }

        for (int i = 0; i < objectsToDeactivate.Length; i++)
        {
            objectsToDeactivate[i].SetActive(true);
        }
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            StartGameNow();
        }
    }

    public void StartGameNow()
    {
        for(int i = 0; i < objectsToActivate.Length; i++)
        {
            objectsToActivate[i].SetActive(true);
        }

        for (int i = 0; i < objectsToDeactivate.Length; i++)
        {
            objectsToDeactivate[i].SetActive(false);
        }
        
        onStartingGame.Invoke();
    }
}
