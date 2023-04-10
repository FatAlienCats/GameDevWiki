# Physics

## The basics 

## Player Movement
```
void Movement3D(vector3 direction, float movementSpeed)
{
        rigidBody.velocity = new Vector3(direction.x * movementSpeed, rigidBody.velocity.y, direction.y * movementSpeed);

}
```
