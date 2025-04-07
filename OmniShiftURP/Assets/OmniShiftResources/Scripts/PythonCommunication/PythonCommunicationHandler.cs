using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PythonCommunicationHandler : MonoBehaviour
{
    [Tooltip("This is a list of the used clients")]
    public Client[] clients;

    public Client activeClient;
    public int index = 0;

    public static PythonCommunicationHandler Instance { get; private set; }

    private void Awake()
    {
        if(Instance != null && Instance != this)
        {
            Destroy(this);
        }
        else
        {
            Instance = this;
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        //activeClient = clients[index];
        activeClient.StartCommunication();
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            ChangeActiveClient(index);
            //activeClient.StopCommunication();
            //index = (index + 1) % clients.Length;
            //activeClient = clients[index];
            //activeClient.StartCommunication();
        }
    }


    public void ChangeActiveClient()
    {
        activeClient.StopCommunication();
        index = (index + 1) % clients.Length;
        activeClient = clients[index];
        activeClient.StartCommunication();
    }


    public void ChangeActiveClient(int index)
    {
        activeClient.StopCommunication();
        this.index = (index + 1) % clients.Length;
        activeClient = clients[this.index];
        activeClient.StartCommunication();
    }
}
