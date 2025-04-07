using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.EventSystems;

public class PlayerController : MonoBehaviour
{

    [Header("Sub Behaviors")]
    public PlayerMovementBehaviour playerMovementBehaviour;
    public PlayerAttackingBehaviour playerAttackBehaviour;


    [Header("Input Settings")]
    public PlayerInput playerInput;
    public float movementSmoothingSpeed = 1f;
    private Vector3 rawInputMovement;
    private Vector3 smoothInputMovement;


    // Action Maps
    private string actionMapPlayerControls = "Player Controls";
    private string actionMapMenuControls = "Menu Controls";

    //Current Control Scheme
    private string currentControlScheme;

    

    private int playerID;

    



    //This is called from the GameManager; when the game is being setup.
    public void SetupPlayer(int newPlayerID)
    {
        playerID = newPlayerID;

        currentControlScheme = playerInput.currentControlScheme;

        playerMovementBehaviour.SetupBehaviour();
        //playerAttackBehaviour.SetUpAttackingBehaviour();
        
    }





    // Start is called before the first frame update
    void Start()
    {
        GetComponent<Rigidbody>();
        transform.parent = GameObject.FindGameObjectWithTag("OmniScene").transform;
    }

    // Update is called once per frame
    void Update()
    {
        CalculateMovementInputSmoothing();
        UpdatePlayerMovement();
        UpdatePlayerAnimationMovement();
    }





    //INPUT SYSTEM ACTION METHODS --------------

    //This is called from PlayerInput; when a joystick or arrow keys has been pushed.
    //It stores the input Vector as a Vector3 to then be used by the smoothing function.


    public void OnMovement(InputAction.CallbackContext value)
    {
        Vector2 inputMovement = value.ReadValue<Vector2>();
        rawInputMovement = new Vector3(-inputMovement.x, inputMovement.y, 0.0f);
    }

    public void OnShoot(InputAction.CallbackContext value)
    {
        if (value.started)
        {
            playerAttackBehaviour.StartAttack();
        }
    }


    //This is called from Player Input, when a button has been pushed, that correspons with the 'TogglePause' action
    //public void OnTogglePause(InputAction.CallbackContext value)
    //{
    //    if (value.started)
    //    {
    //        GameManager.Instance.TogglePauseState(this);
    //    }
    //}

    //INPUT SYSTEM AUTOMATIC CALLBACKS --------------

    //This is automatically called from PlayerInput, when the input device has changed
    //(IE: Keyboard -> Xbox Controller)
    public void OnControlsChanged()
    {

        if (playerInput.currentControlScheme != currentControlScheme)
        {
            currentControlScheme = playerInput.currentControlScheme;

            //playerVisualsBehaviour.UpdatePlayerVisuals();
            RemoveAllBindingOverrides();
        }
    }


    //This is automatically called from PlayerInput, when the input device has been disconnected and can not be identified
    //IE: Device unplugged or has run out of batteries



    public void OnDeviceLost()
    {
        //playerVisualsBehaviour.SetDisconnectedDeviceVisuals();
    }


    public void OnDeviceRegained()
    {
        StartCoroutine(WaitForDeviceToBeRegained());
    }

    IEnumerator WaitForDeviceToBeRegained()
    {
        yield return new WaitForSeconds(0.1f);
        //playerVisualsBehaviour.UpdatePlayerVisuals();
    }




    //Input's Axes values are raw


    void CalculateMovementInputSmoothing()
    {

        smoothInputMovement = Vector3.Lerp(smoothInputMovement, rawInputMovement, Time.deltaTime * movementSmoothingSpeed);

    }

    void UpdatePlayerMovement()
    {
        playerMovementBehaviour.UpdateMovementData(smoothInputMovement);
    }

    void UpdatePlayerAnimationMovement()
    {
        //playerAnimationBehaviour.UpdateMovementAnimation(smoothInputMovement.magnitude);
    }


    public void SetInputActiveState(bool gameIsPaused)
    {
        switch (gameIsPaused)
        {
            case true:
                playerInput.DeactivateInput();
                break;

            case false:
                playerInput.ActivateInput();
                break;
        }
    }

    void RemoveAllBindingOverrides()
    {
        InputActionRebindingExtensions.RemoveAllBindingOverrides(playerInput.currentActionMap);
    }



    //Switching Action Maps ----



    public void EnableGameplayControls()
    {
        playerInput.SwitchCurrentActionMap(actionMapPlayerControls);
    }

    public void EnablePauseMenuControls()
    {
        playerInput.SwitchCurrentActionMap(actionMapMenuControls);
    }


    //Get Data ----
    public int GetPlayerID()
    {
        return playerID;
    }

    public InputActionAsset GetActionAsset()
    {
        return playerInput.actions;
    }

    public PlayerInput GetPlayerInput()
    {
        return playerInput;
    }

}
