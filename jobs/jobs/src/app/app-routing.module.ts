import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { RequestsComponent } from './requests/requests.component';

const routes: Routes = [{ path: '', component: RequestsComponent },
{path : '*', redirectTo : ''},{path : '**', redirectTo : ''}];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
